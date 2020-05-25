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
        fields = ['id', 'name', 'additional_fields']

class RootsSerializer(serializers.ModelSerializer):
    id = serializers.CharField()

    class Meta:
        model = Specification
        fields = ['id', 'name', 'additional_fields']


class TreeSerializer(serializers.ModelSerializer):
    # parent = RecursiveField(many=True, allow_null=True)

    class Meta:
        model = Specification
        fields = ('id', 'name', 'operating_hours', 'first_date', 'link_to_spec', 'additional_fields')


class ComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ('name', 'operating_hours', 'first_date', 'link_to_spec', 'additional_fields')


# class NodeSerializer(serializers.Serializer):

class ObjectDescendants(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ('id', 'name')


class MySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ['id', 'name', 'additional_fields']

    def update(self, instance, validated_data):
        instance.id = validated_data.get('id', instance.id)
        instance.name = validated_data.get('name', instance.name)
        instance.additional_fields = validated_data.get('additional_fields', instance.additional_fields)
        instance.save()
        return instance
