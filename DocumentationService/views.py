from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from DocumentationService.serializers import RootSerializer, ComponentSerializer, TreeSerializer, ObjectDescendants, \
    MySerializer, RootsSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from .models import Specification
from rest_framework.renderers import JSONRenderer
from django.core import serializers
from django.core.files.storage import default_storage, FileSystemStorage
from rest_framework import generics
from rest_framework.parsers import JSONParser, FileUploadParser, MultiPartParser
import json
import time
import datetime


def create_scheduled_task(data):
    pass


# view для работы с Объектами
class ObjectAPI(APIView):

    # Все объекты
    def get(self, request):
        roots = Specification.objects.filter(parent=None)
        serializer = RootSerializer(roots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Удаление объекта
    def delete(self, request):
        Specification.objects.get(id=request.data['id']).delete()
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


# view для работы только с одним объектом (получение данных по id, обновление данных по id)
class ObjectAPIGetChild(APIView):
    # TODO удостовериться в правильности вывода детей
    # Получение данных по id и вывод детей
    def get(self, request, pk):
        nodes = Specification.objects.get(id=pk).get_children()
        # serializer = serializers.serialize('json', nodes)
        # return Response(serializer)
        serializer = ComponentSerializer(nodes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Вывод всех Компонентов Объекта
class ObjectAPIGetDescendants(APIView):

    def get(self, request):
        # nodes = Specification.objects.get_queryset_descendants(Specification.objects.get(id=request.data['id']))
        nodes = Specification.objects.get(id=request.data['id']).get_descendants()
        serializer = ObjectDescendants(nodes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ComponentAPI(APIView):

    # Создание компонента
    # TODO настроить валидацию
    def post(self, request):
        try:
            file = request.FILES['file']
            timestamp = str(int(time.time()))
            name = timestamp + '_' + file.name
            default_storage.save(name=name, content=file)
        except:
            name = ''
        if request.data['operating_hours'] == '':
            op_hours = None
        else:
            op_hours = int(request.data['operating_hours'])
            if request.data['first_date'] == '':
                f_date = None
            else:
                f_date = datetime.datetime.strptime(request.data['first_date'], '%Y%m%d').date()

        node = Specification(name=request.data['name'], operating_hours=op_hours, first_date=f_date,
                             additional_fields=request.data['additional_fields'], link_to_spec=name)
        parent = Specification.objects.get(id=request.data['id'])
        Specification.objects.insert_node(node=node, target=parent, position='first-child', save=True)
        node = Specification.objects.get(id=request.data['id']).get_children().get(name=request.data['name'])
        serializer = TreeSerializer(node)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Обновление Компонента по id
    # TODO настроить валидацию, обновление файлов
    def put(self, request):
        upd_node = Specification.objects.get(id=request.data['id'])
        if request.data['first_date'] == '':
            f_date = None
        else:
            f_date = request.data['first_date']
        if request.data['operating_hours'] == '':
            op_hours = None
        else:
            op_hours = int(request.data['operating_hours'])

        upd_node.name = request.data['name']
        upd_node.operating_hours = op_hours
        upd_node.first_date = f_date
        upd_node.additional_fields = request.data['additional_fields']
        upd_node.save()
        return Response(status=status.HTTP_200_OK)

    # Удаление компонента
    def delete(self, request):
        Specification.objects.get(id=request.data['id']).delete()
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
