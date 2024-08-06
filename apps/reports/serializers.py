from rest_framework import serializers
from .models import Reports
from utils import validates

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

class ReportBatchDeleteSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField(validators=[validates.whether_existed_report_id]), help_text='报告ID列表')

    class Meta:
        fields = ('ids',)

    # def validate_ids(self, value):
    #     for report_id in value:
    #         try:
    #             validates.whether_existed_report_id(report_id)
    #         except:
    #             raise serializers.ValidationError(f"报告ID{report_id}不存在")
    #     return value