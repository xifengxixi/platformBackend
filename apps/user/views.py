from . import serializers
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import generics
from rest_framework_simplejwt.tokens import RefreshToken


class UserViewSet(
    TokenObtainPairView,
    generics.GenericAPIView,
    viewsets.ViewSet,
):

    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    @action(methods=['post'], detail=False)
    def login(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.user
            response_data = serializer.validated_data
            response_data.update({
                'username': user.username,
                'userid': user.id,
            })
            return Response(response_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @action(methods=['post'], detail=False)
    def register(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            user.access = str(refresh.access_token)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False)
    def check_email(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = request.data.get('email')
            count = User.objects.filter(email=email).count()
            return Response({'count': count})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        if self.action == 'login':
            return serializers.UserLoginSerializer
        elif self.action == 'register':
            return serializers.UserRegisterSerializer
        else:
            return serializers.UserCheckEmailSerializer