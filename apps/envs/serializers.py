from rest_framework import serializers
from .models import Envs


class EnvSerializer(serializers.ModelSerializer):

    class Meta:
        model = Envs
        exclude = ('update_time', 'is_delete')
        extra_kwargs = {
            'create_time': {
                'read_only': True,
            }
        }

class EnvNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Envs
        fields = ('id', 'name')

class EnvListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Envs
        exclude = ('update_time', 'is_delete')
        read_only_fields = ('id', 'name', 'base_url', 'desc', 'create_time',)