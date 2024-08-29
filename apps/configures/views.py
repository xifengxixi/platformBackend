from rest_framework import viewsets
from .models import Configures
from .serializers import ConfiguresSerializer
from rest_framework import permissions
from interfaces.models import Interfaces
from utils import handle_datas
import json
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from . import serializers


class ConfiguresViewSet(viewsets.ModelViewSet):

    queryset = Configures.objects.filter(is_delete=False)
    serializer_class = ConfiguresSerializer
    # permission_classes = [permissions.AllowAny]
    ordering_fields = ['id', 'name']
    filterset_fields = ['name',]
    search_fields = ['name', 'author']

    def perform_destroy(self, instance):
        instance.is_delete = True
        instance.save()

    @action(methods=['post'], detail=False)
    def batch_delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            ids = serializer.validated_data.get('ids', [])
            self.get_queryset().filter(id__in=ids).update(is_delete=True)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        config_obj = self.get_object()
        config_request = json.loads(config_obj.request)

        # 处理请求头数据
        config_headers = config_request['config']['request'].get('headers')
        config_headers_list = handle_datas.handle_data4(config_headers)

        # 处理全局变量数据
        config_variables = config_request['config'].get('variables')
        config_variables_list = handle_datas.handle_data2(config_variables)

        author = config_obj.author
        config_name = config_request['config']['name']
        selected_interface_id = config_obj.interface_id
        selected_project_id = Interfaces.objects.get(id=selected_interface_id).project_id

        datas = {
            'author': author,
            'configure_name': config_name,
            'selected_interface_id': selected_interface_id,
            'selected_project_id': selected_project_id,
            'header': config_headers_list,
            'globalVar': config_variables_list
        }

        return Response(datas)

    def get_serializer_class(self):
        if self.action == 'batch_delete':
            return serializers.ConfiguresBatchDeleteSerializer
        else:
            return self.serializer_class