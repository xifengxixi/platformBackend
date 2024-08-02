from rest_framework import serializers
from projects.models import Projects
from interfaces.models import Interfaces
from envs.models import Envs
from testcases.models import Testcases
from configures.models import Configures
from testsuits.models import Testsuits


def whether_existed_project_id(value):
    """
    检查项目id是否存在
    :param value:
    :return:
    """
    if not isinstance(value, int):
        raise serializers.ValidationError('所选项目有误！')
    elif not Projects.objects.filter(is_delete=False, id=value).exists():
        raise serializers.ValidationError('所选项目不存在！')

def whether_existed_interface_id(value):
    """
    检查接口id是否存在
    :param value:
    :return:
    """
    if not isinstance(value, int):
        raise serializers.ValidationError('所选接口有误！')
    elif not Interfaces.objects.filter(is_delete=False, id=value).exists():
        raise serializers.ValidationError('所选接口不存在！')

def whether_existed_env_id(value):
    """
    检查环境配置id是否存在
    :param value:
    :return:
    """
    if value != 0:
        if not Envs.objects.filter(is_delete=False, id=value).exists():
            raise serializers.ValidationError('所选环境配置不存在！')

def whether_existed_testcase_id(value):
    """
    检查用例id是否存在
    :param value:
    :return:
    """
    if not Testcases.objects.filter(is_delete=False, id=value).exists():
        raise serializers.ValidationError('所选用例不存在！')

def whether_existed_configure_id(value):
    """
    检查配置id是否存在
    :param value:
    :return:
    """
    if not Configures.objects.filter(is_delete=False, id=value).exists():
        raise serializers.ValidationError('所选配置不存在！')

def whether_existed_testsuit_id(value):
    """
    检查套件id是否存在
    :param value:
    :return:
    """
    if not Testsuits.objects.filter(is_delete=False, id=value).exists():
        raise serializers.ValidationError('所选套件不存在！')