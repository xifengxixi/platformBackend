from rest_framework import serializers
from .models import Testsuits
from projects.models import Projects
from utils import validates


class TestSuitSerializer(serializers.ModelSerializer):

    project = serializers.StringRelatedField(help_text='所属项目')
    project_id = serializers.PrimaryKeyRelatedField(queryset=Projects.objects.all(), help_text='项目ID')

    class Meta:
        model = Testsuits
        exclude = ('is_delete',)
        extra_kwargs = {
            'include': {
                'write_only': True,
            },
            'create_time': {
                'read_only': True,
            },
            'update_time': {
                'read_only': True,
            }
        }

    def create(self, validated_data):
        validated_data['project'] = validated_data.pop('project_id')
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'project_id' in validated_data:
            validated_data['project'] = validated_data.pop('project_id')
        return super().update(instance, validated_data)

class TestsuitsRunSerializer(serializers.ModelSerializer):
    """
    通过套件来运行测试用例序列化器
    """
    env_id = serializers.IntegerField(write_only=True,
                                      help_text='环境变量ID',
                                      validators=[validates.whether_existed_env_id])

    class Meta:
        model = Testsuits
        fields = ('id', 'env_id')