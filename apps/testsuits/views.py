from rest_framework import viewsets
from .models import Testsuits
from . import serializers
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import action
import os
from django.conf import settings
from datetime import datetime
from envs.models import Envs
from rest_framework import status
from testcases.models import Testcases
from utils import common
from .utils import get_testcases_by_interface_ids


class TestsuitViewSet(viewsets.ModelViewSet):

    queryset = Testsuits.objects.filter(is_delete=False)
    serializer_class = serializers.TestSuitSerializer
    permission_classes = [permissions.AllowAny]
    ordering_fields = ['id', 'name']
    filterset_fields = ['name',]
    search_fields = ['name', 'project__name']

    def perform_destroy(self, instance):
        instance.is_delete = True
        instance.save()

    @action(methods=['post'], detail=False)
    def batch_delete(self, request, *args, **kwargs):
        serializers = self.get_serializer(data=request.data)
        if serializers.is_valid():
            ids = serializers.validated_data.get('ids', [])
            self.get_queryset().filter(id__in=ids).update(is_delete=True)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """获取用例详情信息"""
        testsuit_obj = self.get_object()

        datas = {
            'name': testsuit_obj.name,
            'project_id': testsuit_obj.project_id,
            'include': testsuit_obj.include
        }
        return Response(datas)

    @action(methods=['post'], detail=True)
    def run(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        datas = serializer.validated_data
        env_id = datas.get('env_id')  # 获取环境变量env_id

        # 创建测试用例所在目录名
        testcase_dir_path = os.path.join(settings.SUITES_DIR, datetime.now().strftime('%Y%m%d%H%M%S%f'))
        if not os.path.exists(testcase_dir_path):
            os.mkdir(testcase_dir_path)

        env = Envs.objects.filter(id=env_id, is_delete=False).first()
        include = eval(instance.include)
        if len(include) == 0:
            data_dict = {
                'detail': '此套件下未添加用例，无法运行！'
            }
            return Response(data_dict, status=status.HTTP_400_BAD_REQUEST)

        # 将include中的接口id转化为此接口下的用例id
        include = get_testcases_by_interface_ids(include)
        for testcase_id in include:
            testcase_obj = Testcases.objects.filter(is_delete=False, id=testcase_id).first()
            if testcase_obj:
                common.generate_testcase_files(testcase_obj, env, testcase_dir_path)

        # 运行用例
        return common.run_testcase(instance, testcase_dir_path)

    def get_serializer_class(self):
        """
        不同的action选择不同的序列化器
        :return:
        """
        if self.action == 'run':
            return serializers.TestsuitsRunSerializer
        elif self.action == 'batch_delete':
            return serializers.TestsuitsBatchDeleteSerializer
        else:
            return serializers.TestSuitSerializer