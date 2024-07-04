from rest_framework import serializers
from .models import Testcases
from interfaces.models import Interfaces
from utils import validates


class InterfacesAnotherSerializer(serializers.ModelSerializer):
    project = serializers.StringRelatedField(help_text='项目名称')
    # 项目ID
    pid = serializers.IntegerField(write_only=True, validators=[validates.whether_existed_project_id], help_text='项目ID')
    # 接口ID
    iid = serializers.IntegerField(write_only=True, validators=[validates.whether_existed_interface_id], help_text='接口ID')

    class Meta:
        model = Interfaces
        fields = ('iid', 'name', 'project', 'pid')
        extra_kwargs = {
            'name': {'read_only': True},
        }

    def validate(self, attrs):
        """
        校验项目ID是否与接口ID一致
        :param attrs:
        :return:
        """
        if not Interfaces.objects.filter(id=attrs['iid'], project_id=attrs['pid'], is_delete=False):
            raise serializers.ValidationError('项目和接口信息不对应！')
        return attrs

class TestcasesSerializer(serializers.ModelSerializer):

    interface = InterfacesAnotherSerializer(help_text='所属接口和项目信息')

    class Meta:
        model = Testcases
        fields = ('id', 'name', 'interface', 'include', 'author', 'request')
        extra_kwargs = {
            'include': {'write_only': True},
            'request': {'write_only': True}
        }

    def create(self, validated_data):
        interface_dict = validated_data.pop('interface')
        validated_data['interface_id'] = interface_dict['iid']
        # return super().create(validated_data)
        return Testcases.objects.create(**validated_data)

    def update(self, instance, validated_data):
        if 'interface' in validated_data:
            interface_dict = validated_data.pop('interface')
            validated_data['interface_id'] = interface_dict['iid']
        return super().update(instance, validated_data)

class TestcasesRunSerializer(serializers.ModelSerializer):
    """
    运行测试用例序列化器
    """
    env_id = serializers.IntegerField(write_only=True,
                                      help_text='环境变量ID',
                                      validators=[validates.whether_existed_env_id])

    class Meta:
        model = Testcases
        fields = ('id', 'env_id')

class TestcasesBatchDeleteSerializer(serializers.ModelSerializer):
    """
    批量删除用例序列化器
    """
    ids = serializers.ListField(child=serializers.IntegerField(), required=True, help_text="用例ID列表", write_only=True)

    class Meta:
        model = Testcases
        fields = ('ids',)

    def validate_ids(self, value):
        for testcase_id in value:
            try:
                validates.whether_existed_testcase_id(testcase_id)
            except:
                raise serializers.ValidationError(f"用例ID{testcase_id}不存在")
        return value

class TestcasesNameSerializer(serializers.ModelSerializer):
    """
    用例名称序列化器
    """
    interface_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Testcases
        fields = ('id', 'name', 'interface_id')
        extra_kwargs = {
            'name': {'read_only': True},
        }

    def validate_interface_id(self, value):
        try:
            validates.whether_existed_interface_id(value)
        except:
            raise serializers.ValidationError(f"接口ID{value}不存在")
        return value