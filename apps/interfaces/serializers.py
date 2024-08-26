from rest_framework import serializers
from .models import Interfaces
from projects.models import Projects
from utils import validates


class InterfaceModelSerializer(serializers.ModelSerializer):
    project = serializers.StringRelatedField(help_text='项目名称')
    project_id = serializers.PrimaryKeyRelatedField(queryset=Projects.objects.all(), help_text='项目ID')

    class Meta:
        model = Interfaces
        fields = ('id', 'name', 'project', 'project_id', 'tester', 'desc', 'create_time')
        # exclude = ('update_time', 'is_delete')
        extra_kwargs = {
            'create_time': {
                'read_only': True,
            }
        }

    def create(self, validated_data):
        project = validated_data.pop('project_id')
        validated_data['project'] = project
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'project_id' in validated_data:
            project = validated_data.pop('project_id')
            validated_data['project'] = project
        return super().update(instance, validated_data)

class InterfaceRunSerializer(serializers.ModelSerializer):
    """
    通过接口运行测试用例序列化器
    """
    env_id = serializers.IntegerField(write_only=True,
                                      help_text='环境变量ID',
                                      validators=[validates.whether_existed_env_id])

    class Meta:
        model = Interfaces
        fields = ('id', 'env_id')

class InterfaceListSerializer(serializers.ModelSerializer):
    """
    接口列表序列化器
    """
    project = serializers.StringRelatedField(help_text='项目名称')

    class Meta:
        model = Interfaces
        exclude = ('update_time', 'is_delete')
        read_only_fields = ('id', 'name', 'project', 'tester', 'desc', 'create_time')

class InterfaceBatchDeleteSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(), required=True, help_text='接口ID列表', write_only=True)

    class Meta:
        fields = ('ids',)

    def validate_ids(self, value):
        for interface_id in value:
            try:
                validates.whether_existed_interface_id(interface_id)
            except:
                raise serializers.ValidationError(f'接口ID{interface_id}不存在')
        return value

class InterfaceNamesByIdsSerializer(serializers.ModelSerializer):
    """
    接口名称序列化器
    """
    ids = serializers.ListField(child=serializers.IntegerField(), required=True, help_text='接口ID列表', write_only=True)

    class Meta:
        model = Interfaces
        fields = ('ids', 'id', 'name')
        extra_kwargs = {
            'name': {'read_only': True},
        }