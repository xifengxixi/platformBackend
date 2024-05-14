from rest_framework import viewsets
from .models import DebugTalks
from . import serializers
from rest_framework import permissions
from rest_framework import mixins
from rest_framework import generics
from rest_framework.response import Response

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
