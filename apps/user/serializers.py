from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import serializers

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        # 在响应中添加额外的用户信息或自定义信息
        user = User.objects.get(username=request.data.get('username'))
        response.data['username'] = user.username
        response.data['userid'] = user.id
        return response

# 将自定义的视图类应用到URL
token_obtain_pair = CustomTokenObtainPairView.as_view()

class RegisterSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(
        label='确认密码', min_length=6, max_length=20,
        help_text='确认密码', write_only=True,
        error_messages={
            'min_length': '仅允许6~20个字符的确认密码',
            'max_length': '仅允许6~20个字符的确认密码',
        }
    )
    token = serializers.CharField(label='生成token', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'password_confirm', 'token')
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

        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        user.token = access
        return user