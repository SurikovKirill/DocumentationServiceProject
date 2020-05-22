from rest_framework import serializers
from DocumentationService.models import TaskserviceTask


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskserviceTask
        fields = ['id', 'creation_date', 'ending_date', 'status', 'task_type', 'description', 'report',
                  'link_to_object', 'link_to_component']
