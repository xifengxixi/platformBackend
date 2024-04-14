from rest_framework import serializers
from .models import DebugTalks
from projects.models import Projects


class DebugtalkSerializer(serializers.ModelSerializer):
    project = serializers.StringRelatedField(help_text='项目名称')
    project_id = serializers.PrimaryKeyRelatedField(queryset=Projects.objects.all(), help_text='项目ID')

    class Meta:
        model = DebugTalks
        exclude = ('create_time', 'update_time', 'is_delete')
        extra_kwargs = {
            'debugtalk': {
                'write_only': True,
            }
        }

    def update(self, instance, validated_data):
        if 'project_id' in validated_data:
            validated_data['project'] = validated_data.pop('project_id')
        return super().update(instance, validated_data)