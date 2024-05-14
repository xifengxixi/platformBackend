from rest_framework import viewsets
from .models import Envs
from . import serializers
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response


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
        else:
            return self.serializer_class