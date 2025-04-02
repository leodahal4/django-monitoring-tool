"""example_project URL Configuration"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('monitoring/', include('django_health_metrics.urls')),
]