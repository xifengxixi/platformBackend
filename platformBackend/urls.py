from django.contrib import admin
from django.urls import path, include
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path('docs/', include_docs_urls(title='测试平台接口文档', description='这是一个美轮美奂的接口文档平台')),
    path('', include('user.urls')),
    path('', include('projects.urls')),
    path('', include('interfaces.urls')),
    path('', include('envs.urls')),
    path('', include('debugtalks.urls')),
    path('', include('testsuits.urls')),
    path('', include('reports.urls')),
    path('', include('configures.urls')),
    path('', include('testcases.urls')),
    path('', include('summary.urls')),
]