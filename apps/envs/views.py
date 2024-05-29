from rest_framework import viewsets
from .models import Envs
from . import serializers
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


class EnvViewSet(viewsets.ModelViewSet):

    queryset = Envs.objects.filter(is_delete=False)
    serializer_class = serializers.EnvSerializer
    permission_classes = [permissions.AllowAny]
    ordering_fields = ['id', 'name']

    def perform_destroy(self, instance):
        instance.is_delete = True
        instance.save()

    @action(detail=False)
    def names(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(instance=queryset, many=True)
        return Response(serializer.data)
        # env_objs = self.get_queryset()
        # name_list = []
        # for obj in env_objs:
        #     name_list.append({
        #         'id': obj.id,
        #         'name': obj.name
        #     })
        # return Response(name_list)

    def get_serializer_class(self):
        if self.action == 'names':
            return serializers.EnvNameSerializer
        elif self.action == 'get_list':
            return serializers.EnvListSerializer
        elif self.action == 'batch_delete':
            return serializers.EnvBatchDeleteSerializer
        else:
            return self.serializer_class

    @action(methods=['post'], detail=False)
    def get_list(self, request, *args, **kwargs):
        filter_args = {
            'name__contains': request.data.get('name'),
            'base_url__contains': request.data.get('base_url'),
            'desc__contains': request.data.get('desc'),
        }

        queryset = self.get_queryset().filter(**filter_args)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['post'], detail=False)
    def batch_delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            ids = serializer.validated_data.get('ids', [])
            self.get_queryset().filter(id__in=ids).update(is_delete=True)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)