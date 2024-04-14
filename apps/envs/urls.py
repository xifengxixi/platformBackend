from rest_framework import routers
from . import views
from django.urls import path, include


router = routers.DefaultRouter()
router.register(r'envs', views.EnvViewSet)

urlpatterns = [
    path('', include(router.urls)),
]