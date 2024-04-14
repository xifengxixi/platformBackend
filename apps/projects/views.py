from . import serializers
from .models import Projects
from interfaces.models import Interfaces
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from .utils import get_count_by_project
import os
from django.conf import settings
import time
from envs.models import Envs
from rest_framework import status
from testcases.models import Testcases
from utils import common


class ProjectsViewSet(viewsets.ModelViewSet):

    queryset = Projects.objects.filter(is_delete=False)
    serializer_class = serializers.ProjectModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ['id', 'name']

    def perform_destroy(self, instance):
        instance.is_delete = True
        instance.save() # 逻辑删除

    @action(methods=['get'], detail=False)
    def names(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # serializer = serializers.ProjectNameSerializer(instance=queryset, many=True)
        serializer = self.get_serializer(instance=queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def interfaces(self, request, *args, **kwargs):
        interface_objs = Interfaces.objects.filter(project_id=kwargs.get('pk'), is_delete=False)
        interface_list = []
        for obj in interface_objs:
            interface_list.append({
                'id': obj.id,
                'name': obj.name
            })
        return Response(interface_list)

    def list(self, request, *args, **kwargs):
        # queryset = self.filter_queryset(self.get_queryset())
        #
        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     datas = serializer.data
        #     datas = get_count_by_project(datas)
        #     return self.get_paginated_response(datas)
        #
        # serializer = self.get_serializer(queryset, many=True)
        # datas = serializer.data
        # datas = get_count_by_project(datas)
        # return Response(datas)
        response = super().list(self, request, *args, **kwargs)
        response.data['results'] = get_count_by_project(response.data['results'])
        return response

    # def get_serializer_class(self):
    #     if self.action == 'names':
    #         return serializers.ProjectNameSerializer
    #     else:
    #         return self.serializer_class

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
        interface_objs = Interfaces.objects.filter(is_delete=False, project=instance)

        if not interface_objs.exists(): # 如果此项目下没有接口，则无法运行
            data_dict = {
                'detail': '此项目下无接口，无法运行！'
            }
            return Response(data_dict, status=status.HTTP_400_BAD_REQUEST)

        for inter_obj in interface_objs:
            testcase_objs = Testcases.objects.filter(is_delete=False, interface=inter_obj)

            for one_obj in testcase_objs:
                common.generate_testcase_files(one_obj, env, testcase_dir_path)

        # 运行用例
        return common.run_testcase(instance, testcase_dir_path)

    def get_serializer_class(self):
        """
        不同的action选择不同的序列化器
        :return:
        """
        if self.action == 'names':
            return serializers.ProjectNameSerializer
        elif self.action == 'run':
            return serializers.ProjectsRunSerializer
        else:
            return self.serializer_class