from rest_framework import viewsets
from rest_framework import permissions
from .models import Interfaces
from . import serializers
from rest_framework.decorators import action
from testcases.models import Testcases
from configures.models import Configures
from .utils import get_count_by_interface
from rest_framework.response import Response
import os
from django.conf import settings
import time
from envs.models import Envs
from rest_framework import status
from utils import common


class InterfacesViewSet(viewsets.ModelViewSet):

    queryset = Interfaces.objects.filter(is_delete=False)
    serializer_class = serializers.InterfaceModelSerializer
    permission_classes = [permissions.AllowAny]
    ordering_fields = ['id', 'name']

    def perform_destroy(self, instance):
        instance.is_delete = True
        instance.save()

    @action(methods=['get'], detail=True)
    def testcases(self, request, pk):
        testcase_objs = Testcases.objects.filter(interface_id=pk, is_delete=False)
        testcase_list = []
        for obj in testcase_objs:
            testcase_list.append({
                'id': obj.id,
                'name': obj.name
            })
        return Response(testcase_list)

    @action(detail=True)
    def configures(self, request, pk):
        configures_objs = Configures.objects.filter(interface_id=pk, is_delete=False)
        configures_list = []
        for obj in configures_objs:
            configures_list.append({
                'id': obj.id,
                'name': obj.name
            })
        return Response(configures_list)

    def list(self, request, *args, **kwargs):
        response = super().list(self, request, *args, **kwargs)
        response.data['results'] = get_count_by_interface(response.data['results'])
        return response

    @action(methods=['post'], detail=True)
    def run(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        datas = serializer.validated_data
        env_id = datas.get('env_id') # 获取环境变量env_id

        # 创建测试用例所在目录名
        testcase_dir_path = os.path.join(settings.SUITES_DIR, time.strftime('%Y%m%d%H%M%S%f'))
        if not os.path.exists(testcase_dir_path):
            os.mkdir(testcase_dir_path)

        env = Envs.objects.filter(id=env_id, is_delete=False).first()
        testcase_objs = Testcases.objects.filter(is_delete=False, interface=instance)

        if not testcase_objs.exists():  # 如果此接口下没有用例，则无法运行
            data_dict = {
                'detail': '此接口下无用例，无法运行！'
            }
            return Response(data_dict, status=status.HTTP_400_BAD_REQUEST)

        for one_obj in testcase_objs:
            common.generate_testcase_files(one_obj, env, testcase_dir_path)

        # 运行用例
        return common.run_testcase(instance, testcase_dir_path)

    def get_serializer_class(self):
        """
        不同的action选择不同的序列化器
        :return:
        """
        return serializers.InterfaceRunSerializer if self.action == 'run' else self.serializer_class