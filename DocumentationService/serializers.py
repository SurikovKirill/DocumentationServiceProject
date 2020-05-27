from rest_framework import serializers
from DocumentationService.models import Specification


class RootSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ['id', 'name', 'additional_fields']


class ComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ('id', 'name', 'operating_hours', 'first_date', 'link_to_spec', 'additional_fields')


class ObjectDescendants(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ('id', 'name')
