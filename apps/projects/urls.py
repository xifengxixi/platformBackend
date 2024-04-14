from django.urls import path, include
from projects import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'projects', views.ProjectsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]