from rest_framework import viewsets
from .models import DebugTalks
from . import serializers
from rest_framework import permissions
from rest_framework import mixins
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import action

class DebugtalkViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    generics.GenericAPIView,
    viewsets.ViewSet,
):

    queryset = DebugTalks.objects.filter(is_delete=False)
    serializer_class = serializers.DebugtalkSerializer
    permission_classes = [permissions.AllowAny]
    ordering_fields = ['id', 'name']

    def retrieve(self, request, *args, **kwargs):
        # instance = self.get_object()
        # serializer = self.get_serializer(instance)
        # data = serializer.data
        # data['debugtalk'] = instance.debugtalk
        # return Response(data)
        response = super().retrieve(request, *args, **kwargs)
        response.data['debugtalk'] = self.get_object().debugtalk
        return response

    @action(methods=['post'], detail=False)
    def get_list(self, request, *args, **kwargs):
        filter_args = {
            'project__name__contains': request.data.get('project', ''),
        }

        queryset = self.get_queryset().filter(**filter_args)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
