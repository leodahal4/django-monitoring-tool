from django.apps import AppConfig

class HealthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_health_metrics'
    verbose_name = 'Health Metrics'