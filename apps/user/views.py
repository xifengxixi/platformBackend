from rest_framework.generics import CreateAPIView
from . import serializers

class RegisterView(CreateAPIView):
    serializer_class = serializers.RegisterSerializer
