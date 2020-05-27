from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from DocumentationService.serializers import RootSerializer, ComponentSerializer, ObjectDescendants
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Specification
from rest_framework.renderers import JSONRenderer
from django.core import serializers
from django.core.files.storage import default_storage, FileSystemStorage
from rest_framework import generics
from rest_framework.parsers import JSONParser, FileUploadParser, MultiPartParser
import json
import time
import datetime
import requests


def create_scheduled_task(component, object_data, first_date, name):
    req = requests.post('http://127.0.0.1:8000/api/tasks/manager',
                        data={'component': component, 'object_data': object_data,
                              'creation_date': first_date, 'status': 'PLANNED', 'task_type': 'SCHEDULED',
                              'description': 'Плановое техобслуживание для {0}'.format(name)})
    req.raise_for_status()
    # id компонента
    # название компонента
    # id объекта
    # название объекта
    # first_date
    # creation_date
    # status
    # task_type
    # description ""


def delete_scheduled_tasks(id, descendants):
    req = requests.delete('http://127.0.0.1:8000/api/tasks/manager',
                          data={'id': id, 'descendants': descendants})
    req.raise_for_status()


def delete_scheduled_tasks_for_object(id, descendants):
    req = requests.delete('http://127.0.0.1:8000/api/tasks/manager',
                          data={'id': id, 'descendants': descendants})
    req.raise_for_status()


# если пришел запрос на удаление объекта или компонента, то
# 1 находим всех descendants
# 2 отправляем запрос на удаление плановых задач на сервис задач, в теле указываем id всех descendants, включая родителя
# 3 на сервисе задач удаляем все плановые задачи, имеющие в себе id компонента и id объекта


class ObjectAPI(APIView):

    # Все объекты
    def get(self, request):
        roots = Specification.objects.filter(parent=None)
        serializer = RootSerializer(roots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # TODO при удалении объекта удалить все плановые задачи для его компонентов
    # Удаление объекта
    def delete(self, request):
        try:
            id = request.data['id']
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        Specification.objects.get(id=id).delete()
        Specification.objects.rebuild()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # Создание объекта
    def post(self, request):
        serializer = RootSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Редактирование Объекта
class ObjectAPIUpdate(generics.UpdateAPIView):
    queryset = Specification.objects.all()
    serializer_class = RootSerializer


class ObjectAPIGetChild(APIView):
    # Получение данных по id и вывод детей
    def get(self, request, pk):
        nodes = Specification.objects.get(id=pk).get_children()
        serializer = ComponentSerializer(nodes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ObjectAPIGetDescendants(APIView):
    # Вывод всех компонентов, из которых состоит объект
    def get(self, request):
        try:
            id = request.data['id']
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        nodes = Specification.objects.get(id=id).get_descendants()
        serializer = ObjectDescendants(nodes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ComponentAPI(APIView):

    # TODO при создании компонента с полями operating_hours и first_data
    #  отправлять запрос на сервис задач для добавления плановой задачи
    # Создание компонента
    def post(self, request):
        try:
            name = request.data['name']
            id = request.data['id']
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            file = request.FILES['file']
            timestamp = str(int(time.time()))
            filename = timestamp + '_' + file.name
            default_storage.save(name=filename, content=file)
        except:
            filename = None
        try:
            operating_hours = int(request.data['operating_hours'])
            first_date = datetime.datetime.strptime(request.data['first_date'], '%Y%m%d').date()
        except:
            operating_hours = None
            first_date = None
        try:
            additional_fields = json.loads(request.data['additional_fields'])
        except:
            additional_fields = None

        node = Specification(name=name, operating_hours=operating_hours, first_date=first_date,
                             additional_fields=additional_fields, link_to_spec=filename)
        parent = Specification.objects.get(id=id)
        Specification.objects.insert_node(node=node, target=parent, position='first-child', save=True)
        node = Specification.objects.get(id=id).get_children().get(name=name)
        # //////////////////////////////////////////////
        if operating_hours is not None:
            print("create_scheduled_task")
        # //////////////////////////////////////////////
        serializer = ComponentSerializer(node)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Обновление Компонента по id
    # TODO настроить валидацию, обновление файлов, добавление/удаление задач в сервисе задач
    def put(self, request):
        try:
            name = request.data['name']
            id = request.data['id']
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            operating_hours = int(request.data['operating_hours'])
            first_date = datetime.datetime.strptime(request.data['first_date'], '%Y%m%d').date()
        except:
            operating_hours = None
            first_date = None
        try:
            additional_fields = json.loads(request.data['additional_fields'])
        except:
            additional_fields = None

        upd_node = Specification.objects.get(id=id)
        try:
            file = request.FILES['file']
            timestamp = str(int(time.time()))
            filename = timestamp + '_' + file.name
            default_storage.save(name=filename, content=file)
            default_storage.delete(upd_node.link_to_spec)
        except:
            filename = upd_node.link_to_spec
        upd_node.name = name
        if (upd_node.operating_hours is not None) and (operating_hours is None):
            print("delete_scheduled_task")
        if (upd_node.operating_hours is None) and (operating_hours is not None):
            print("create_scheduled_task")
        upd_node.operating_hours = operating_hours
        upd_node.first_date = first_date
        upd_node.additional_fields = additional_fields
        upd_node.link_to_spec = filename
        upd_node.save()
        return Response(status=status.HTTP_200_OK)

    # Удаление компонента
    # TODO удаление задач в сервисе задач
    def delete(self, request):
        try:
            id = request.data['id']
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        Specification.objects.get(id=id).delete()
        print("delete_scheduled_task")
        Specification.objects.rebuild()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Информация о компоненте
class ComponentAPIGetInfo(generics.RetrieveAPIView):
    queryset = Specification.objects.all()
    serializer_class = ComponentSerializer


class ComponentAPIGetChildren(APIView):
    # Вывод детей компонента
    def get(self, request, pk):
        nodes = Specification.objects.get(id=pk).get_children()
        serializer = ComponentSerializer(nodes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
