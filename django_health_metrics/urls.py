from django.urls import path
from .views import metrics_view, health_view

urlpatterns = [
    path('metrics/', metrics_view, name='metrics'),
    path('health/', health_view, name='health'),
]
