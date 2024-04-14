from rest_framework import routers
from . import views
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'configures', views.ConfiguresViewSet)

urlpatterns = [
    path('', include(router.urls)),
]