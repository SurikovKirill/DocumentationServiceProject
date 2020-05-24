from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from DocumentationService.serializers import RootSerializer, ComponentSerializer, TreeSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from .models import Specification
from rest_framework.renderers import JSONRenderer
from django.core import serializers

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


# view для работы только с одним объектом (получение данных по id, обновление данных по id)
class ObjectAPIGet(APIView):
    # Получение данных по id и вывод ближайших детей
    def get(self, request, pk):
        nodes = Specification.objects.get(id=pk).get_descendants(include_self=True)
        serializer = serializers.serialize('json', nodes)
        return Response(serializer, status=status.HTTP_200_OK)

    # Обновление данных по id
    def put(self, request):
        pass


class InsertationRoot(APIView):

    def post(self, request):
        node = Specification.objects.create(name=request.data['name'], operating_hours=request.data['operating_hours'], first_date=request.data['first_date'], additional_fields=request.data['additional_fields'], parent=Specification.objects.get(id=request.data['parent']) )
        Response(status=status.HTTP_200_OK)


class SpecViewSet(viewsets.ModelViewSet):
    queryset = Specification.objects.all()
    serializer_class = RootSerializer


#
class ComponentView(APIView):

    def get(self, request, pk):
        try:
            component = Specification.objects.get(id=pk)
        except:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            serializer = ComponentSerializer(component)
            return Response(serializer.data, status=status.HTTP_200_OK)

