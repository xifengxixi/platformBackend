from rest_framework import serializers
from .models import Reports


class ReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reports
        exclude = ('update_time', 'is_delete')
        read_only_fields = ('name', 'result', 'count', 'success', 'summary', 'create_time')
        extra_kwargs = {
            'html': {
                'write_only': True,
            }
        }