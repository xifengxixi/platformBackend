from rest_framework import viewsets
from .models import Testcases
from .serializers import TestcasesSerializer, TestcasesRunSerializer
from rest_framework import permissions
from interfaces.models import Interfaces
from utils import handle_datas
import json
from rest_framework.response import Response
from rest_framework.decorators import action
import os
import time
from django.conf import settings
from envs.models import Envs
from utils import common

class TestcasesViewSet(viewsets.ModelViewSet):

    queryset = Testcases.objects.filter(is_delete=False)
    serializer_class = TestcasesSerializer
    permission_classes = [permissions.AllowAny]
    ordering_fields = ['id', 'name']

    def perform_destroy(self, instance):
        instance.is_delete = True
        instance.save()

    def retrieve(self, request, *args, **kwargs):
        """获取用例详情信息"""

        testcase_obj = self.get_object()

        # 用例前置信息
        testcase_include = json.loads(testcase_obj.include)

        # 用例请求信息
        testcase_request = json.loads(testcase_obj.request)
        testcase_request_datas = testcase_request.get('test').get('request')

        # 处理用例的headers列表
        testcase_headers = testcase_request_datas.get('headers')
        testcase_headers_list = handle_datas.handle_data4(testcase_headers)

        # 处理用例的parmas数据
        testcase_params = testcase_request_datas.get('params')
        testcase_params_list = handle_datas.handle_data4(testcase_params)

        # 处理form表单数据
        testcase_form_datas = testcase_request_datas.get('data')
        testcase_form_datas_list = handle_datas.handle_data6(testcase_form_datas)

        # 处理json数据
        testcase_json_datas = json.dumps(testcase_request_datas.get('json'))

        # 处理用例variables变量列表
        testcase_variables = testcase_request.get('test').get('variables')
        testcase_variables_list = handle_datas.handle_data2(testcase_variables)

        # 处理extract数据
        testcase_extract_datas = testcase_request.get('test').get('extract')
        testcase_extract_datas_list = handle_datas.handle_data3(testcase_extract_datas)

        # 处理用例的validate列表
        testcase_validate = testcase_request.get('test').get('validate')
        testcase_validate_list = handle_datas.handle_data1(testcase_validate)

        # 处理parameters数据
        testcase_parameters_datas = testcase_request.get('test').get('parameters')
        testcase_parameters_datas_list = handle_datas.handle_data3(testcase_parameters_datas)

        # 处理setupHooks数据
        testcase_setup_hooks_datas = testcase_request.get('test').get('setup_hooks')
        testcase_setup_hooks_datas_list = handle_datas.handle_data5(testcase_setup_hooks_datas)

        # 处理teardownHooks数据
        testcase_teardown_hooks_datas = testcase_request.get('test').get('teardown_hooks')
        testcase_teardown_hooks_datas_list = handle_datas.handle_data5(testcase_teardown_hooks_datas)

        selected_configure_id = testcase_include.get('config')
        selected_interface_id = testcase_obj.interface_id
        selected_project_id = Interfaces.objects.get(id=selected_interface_id).project_id
        selected_testcase_id = testcase_include.get('testcases')

        datas = {
            'author': testcase_obj.author,
            'testcase_name': testcase_obj.name,
            'selected_configure_id': selected_configure_id,
            'selected_interface_id': selected_interface_id,
            'selected_project_id': selected_project_id,
            'selected_testcase_id': selected_testcase_id,

            'method': testcase_request_datas.get('method'),
            'url': testcase_request_datas.get('url'),
            'param': testcase_params_list,
            'header': testcase_headers_list,
            'variable': testcase_form_datas_list,
            'jsonVariable': testcase_json_datas,

            'extract': testcase_extract_datas_list,
            'validate': testcase_validate_list,
            'globalVar': testcase_variables_list,
            'parameterized': testcase_parameters_datas_list,
            'setupHooks': testcase_setup_hooks_datas_list,
            'teardownHooks': testcase_teardown_hooks_datas_list,
        }
        return Response(datas)

    @action(methods=['post'], detail=True)
    def run(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        datas = serializer.validated_data

        env_id = datas.get('env_id')
        testcase_dir_path = os.path.join(settings.SUITES_DIR, time.strftime('%Y%m%d%H%M%S%f'))
        os.mkdir(testcase_dir_path)

        env = Envs.objects.filter(id=env_id, is_delete=False).first()

        # 生成yaml用例文件
        common.generate_testcase_files(instance, env, testcase_dir_path)

        # 运行用例
        return common.run_testcase(instance, testcase_dir_path)


    def get_serializer_class(self):
        return TestcasesRunSerializer if self.action == 'run' else self.serializer_class

    @action(methods=['post'], detail=False)
    def get_list(self, request, *args, **kwargs):
        filter_args = {
            'name__contains': request.data.get('name', ''),
            'interface__name__contains': request.data.get('interface', ''),
            'project__name__contains': request.data.get('project', ''),
        }
        queryset = self.get_queryset().filter(**filter_args)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)