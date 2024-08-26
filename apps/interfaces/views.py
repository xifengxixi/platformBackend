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
from datetime import datetime
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

    @action(methods=['post'], detail=False)
    def batch_delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            ids = request.data.get('ids', [])
            Interfaces.objects.filter(id__in=ids).update(is_delete=True)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

    @action(methods=['post'], detail=False)
    def get_list(self, request, *args, **kwargs):
        filter_args = {
            'name__contains': request.data.get('name', ''),
        }

        queryset = self.get_queryset().filter(**filter_args)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            datas = serializer.data
            datas = get_count_by_interface(datas)
            return self.get_paginated_response(datas)

        serializer = self.get_serializer(queryset, many=True)
        datas = serializer.data
        datas = get_count_by_interface(datas)
        return Response(datas)

    @action(methods=['post'], detail=True)
    def run(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        datas = serializer.validated_data
        env_id = datas.get('env_id') # 获取环境变量env_id

        # 创建测试用例所在目录名
        testcase_dir_path = os.path.join(settings.SUITES_DIR, datetime.now().strftime('%Y%m%d%H%M%S%f'))
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

    @action(methods=['post'], detail=False)
    def names_by_ids(self, request, *args, **kwargs):
        ids = request.data.get('ids', [])
        ids = ids if ids else []
        queryset = self.get_queryset().filter(id__in=ids)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        """
        不同的action选择不同的序列化器
        :return:
        """
        if self.action == 'run':
            return serializers.InterfaceRunSerializer
        elif self.action == 'get_list':
            return serializers.InterfaceListSerializer
        elif self.action == 'batch_delete':
            return serializers.InterfaceBatchDeleteSerializer
        elif self.action == 'names_by_ids':
            return serializers.InterfaceNamesByIdsSerializer
        else:
            return self.serializer_class