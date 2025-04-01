from django.contrib import admin
from django.urls import path
from health.views import metrics_view, health_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('metrics/', metrics_view, name='metrics'),
    path('health/', health_view, name='health'),
]