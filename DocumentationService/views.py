from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from DocumentationService.serializers import RootSerializer, ComponentSerializer, TreeSerializer, ObjectDescendants
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from .models import Specification
from rest_framework.renderers import JSONRenderer
from django.core import serializers
from django.core.files.storage import default_storage
from rest_framework.parsers import JSONParser, FileUploadParser, MultiPartParser

# view для работы с Объектами (без получения объекта по id)
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

    # Обновление данных по id
    def put(self, request):
        root = Specification.objects.get(id=request.data['id'])
        root.name = request.data['name']
        root.additional_fields = request.data['additional_fields']
        root.save()
        return Response(status=status.HTTP_200_OK)


# view для работы только с одним объектом (получение данных по id, обновление данных по id)
class ObjectAPIGet(APIView):
    # TODO удостовериться в правильности вывода детей
    # Получение данных по id и вывод детей
    def get(self, request, pk):
        nodes = Specification.objects.get(id=pk).get_children()
        serializer = serializers.serialize('json', nodes)
        return Response(serializer, status=status.HTTP_200_OK)


class NodeViewSet(viewsets.ModelViewSet):
    queryset = Specification.objects.all()
    serializer_class = RootSerializer


class ComponentView(APIView):
    def get(self, request):
        # nodes = Specification.objects.get_queryset_descendants(Specification.objects.get(id=request.data['id']))
        nodes = Specification.objects.get(id=request.data['id']).get_descendants()
        serializer = ObjectDescendants(nodes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Создание компонента
    # TODO настроить валидацию, работу с файлами
    def post(self, request):
        file = request.FILES['file']
        default_storage.save("home/specs/" + file.name, file)
        if request.data['operating_hours'] == '':
            op_hours = None
        else:
            op_hours = int(request.data['operating_hours'])
        if request.data['first_date'] == '':
            f_date = None
        else:
            f_date = request.data['operating_hours']
        node = Specification(name=request.data['name'], operating_hours=op_hours, first_date=f_date,
                             additional_fields=request.data['additional_fields'], link_to_spec=file.name)
        parent = Specification.objects.get(id=request.data['id'])
        Specification.objects.insert_node(node=node, target=parent, position='first-child', save=True)
        return Response(status=status.HTTP_200_OK)

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
        upd_node.operating_hours=op_hours
        upd_node.first_date = f_date
        upd_node.additional_fields = request.data['additional_fields']
        upd_node.save()
        return Response(status=status.HTTP_200_OK)

    # Удаление компонента
    # TODO проверить каскадное удаление
    def delete(self, request):
        Specification.objects.get(id=request.data['id']).delete()
        Specification.objects.rebuild()
        return Response(status=status.HTTP_204_NO_CONTENT)

# view для работы только с одним компонентом (получение данных по id, обновление данных по id)
class ComponentViewGet(APIView):
    # TODO вывод детей
    # Получение данных по id и вывод детей
    def get(self, request, pk):
        try:
            component = Specification.objects.get(id=pk)
        except:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            serializer = ComponentSerializer(component)
            return Response(serializer.data, status=status.HTTP_200_OK)

