from django.urls import path, include
# from rest_framework_simplejwt.views import token_obtain_pair
from .serializers import token_obtain_pair
from . import views

urlpatterns = [
    path('user/login/', token_obtain_pair),
    path('user/register/', views.RegisterView.as_view()),
]