import json
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import generics
from .models import Reports
from . import serializers
from rest_framework import permissions
from rest_framework.decorators import action
import re
import os
from platformBackend import settings
from time import strftime
from django.http import StreamingHttpResponse
from .utils import get_file_contents
from django.utils.encoding import escape_uri_path
from rest_framework.response import Response


class ReportViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.ViewSet,
    generics.GenericAPIView,
):

    queryset = Reports.objects.filter(is_delete=False)
    serializer_class = serializers.ReportSerializer
    permission_classes = [permissions.AllowAny]
    ordering_fields = ('id', 'name')

    def perform_destroy(self, instance):
        instance.is_delete = True
        instance.save()

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        for i in response.data['results']:
            i['result'] = 'Pass' if i['result'] else 'Fail'
        return response

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        datas = serializer.data
        try:
            datas['summary'] = json.loads(datas['summary'], encoding='utf-8')
        except Exception as e:
            pass
        return Response(datas)

    @action(detail=True)
    def download(self, request, pk=None):
        instance = self.get_object()
        html = instance.html
        name = instance.name
        match = re.match(r'(.*_)\d+', name)
        if match:
            match = match.group(1)
            # 创建报告路径
            report_filename = f'{match}{strftime("%Y%m%d%H%M%S")}.html'
        else:
            report_filename = name

        report_path = os.path.join(settings.REPORTS_DIR, report_filename)  # 报告最终路径

        # 将报告保存到reports目录下
        with open(report_path, 'w+', encoding='utf-8') as f:
            f.write(html)

        response = StreamingHttpResponse(get_file_contents(report_path))
        report_path_final = escape_uri_path(report_filename)  # 支持中文，防止乱码
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = f'attachment; filename*=UTF-8 {report_path_final}'
        return response