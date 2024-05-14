from rest_framework import serializers
from .models import Projects
from interfaces.models import Interfaces
from debugtalks.models import DebugTalks
from utils import validates


class ProjectModelSerializer(serializers.ModelSerializer):

    # create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Projects
        exclude = ('update_time', 'is_delete')
        extra_kwargs = {
            'create_time': {
                'read_only': True,
            }
        }

    def create(self, validated_data):
        project_obj = super().create(validated_data)
        DebugTalks.objects.create(project=project_obj)
        return project_obj

class ProjectNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Projects
        fields = ('id', 'name')

class InterfaceNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Interfaces
        fields = ('id', 'name', 'tester')

class InterfacesByProjectIdSerializer(serializers.ModelSerializer):
    interfaces = InterfaceNameSerializer(read_only=True, many=True)

    class Meta:
        model = Projects
        fields = ('id', 'interfaces')

class ProjectsRunSerializer(serializers.ModelSerializer):
    """
    通过项目运行测试用例序列化器
    """
    env_id = serializers.IntegerField(write_only=True,
                                      help_text='环境变量ID',
                                      validators=[validates.whether_existed_env_id])

    class Meta:
        model = Projects
        fields = ('id', 'env_id')

class ProjectsBatchDeleteSerializer(serializers.Serializer):
    """
    批量删除项目序列化器
    """
    ids = serializers.ListField(child=serializers.IntegerField(), required=True, help_text='项目ID列表', write_only=True)

    class Meta:
        model = Projects
        fields = ('ids',)

    def validate_ids(self, value):

        # 校验项目是否存在
        for project_id in value:
            try:
                validates.whether_existed_project_id(project_id)
            except:
                raise serializers.ValidationError(f'项目ID{project_id}不存在')
        return value

class ProjectsListSerializer(serializers.ModelSerializer):
    """
    项目列表序列化器
    """

    class Meta:
        model = Projects
        exclude = ('update_time', 'is_delete')
        read_only_fields = ('id', 'name', 'leader', 'tester', 'programmer', 'publish_app', 'desc', 'create_time')