from rest_framework import serializers
from DocumentationService.models import TaskserviceTask, Specification
from rest_framework_recursive.fields import RecursiveField


# class TaskSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TaskserviceTask
#         fields = ['id', 'creation_date', 'ending_date', 'status', 'task_type', 'description', 'report',
#                   'link_to_object', 'link_to_component']


class RootSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ('id', 'name', 'additional_fields')

class TreeSerializer(serializers.ModelSerializer):
    parent = RecursiveField(many=True, allow_null=True)

    class Meta:
        model = Specification
        fields = ('id', 'name', 'additional_fields', 'parent')


class ComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ('id', 'name', 'operating_hours', 'first_date', 'link_to_spec', 'additional_fields', 'parent')
