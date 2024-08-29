from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserLoginSerializer(TokenObtainPairSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {
            'username': {
                'read_only': True
            },
            'password': {
                'read_only': True
            }
        }


class UserRegisterSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(
        label='确认密码', min_length=6, max_length=20,
        help_text='确认密码', write_only=True,
        error_messages={
            'min_length': '仅允许6~20个字符的确认密码',
            'max_length': '仅允许6~20个字符的确认密码',
        }
    )
    access = serializers.CharField(label='生成token', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'password_confirm', 'access')
        extra_kwargs = {
            'username': {
                'label': '用户名',
                'help_text': '用户名',
                'required': True,
                'min_length': 6,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许6~20个字符的用户名',
                    'max_length': '仅允许6~20个字符的用户名',
                }
            },
            'email': {
                'label': '邮箱',
                'help_text': '邮箱',
                'write_only': True,
                'required': True,
            },
            'password': {
                'label': '密码',
                'help_text': '密码',
                'write_only': True,
                'min_length': 6,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许6~20个字符的密码',
                    'max_length': '仅允许6~20个字符的密码',
                }
            },
        }

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError('密码和确认密码不一致')
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user