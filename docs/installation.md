# Installation

This guide explains how to install and set up the `django-health-metrics` package in your Django project.

## Prerequisites
- Python 3.6 or higher
- Django 3.2 or higher
- pip (Python package manager)

## Install the Package
You can install `django-health-metrics` via pip:

```bash
pip install django-health-metrics
```

### Optional Dependencies
The package supports various health checks (e.g., Redis, MongoDB). Install additional dependencies as needed:

- Redis: `pip install django-health-metrics[redis]`
- Elasticsearch: `pip install django-health-metrics[elasticsearch]`
- RabbitMQ: `pip install django-health-metrics[rabbitmq]`
- Celery: `pip install django-health-metrics[celery]`
- MongoDB: `pip install django-health-metrics[mongodb]`
- Custom URL checks: `pip install django-health-metrics[requests]`

For all features: 
```bash
pip install django-health-metrics[redis,elasticsearch,rabbitmq,celery,mongodb,requests]
```

## Add to Django Project
1. **Add to INSTALLED_APPS**  
   In your Django project's `settings.py`, add `django_health_metrics` to the `INSTALLED_APPS` list:

   ```python
   INSTALLED_APPS = [
       # ... other apps ...
       'django_health_metrics',
   ]
   ```

2. **Configure URLs**  
   Include the app’s URLs in your project’s `urls.py`:

   ```python
   from django.urls import path, include

   urlpatterns = [
       # ... other URL patterns ...
       path('monitoring/', include('django_health_metrics.urls')),
   ]
   ```

## Configuration
Customize the health checks by adding these optional settings to your `settings.py`:

```python
# Enable/disable specific health checks
ENABLE_REDIS_CHECK = True
ENABLE_DB_CHECK = True
ENABLE_CACHE_CHECK = False
ENABLE_ELASTICSEARCH_CHECK = False
ENABLE_RABBITMQ_CHECK = False
ENABLE_CELERY_CHECK = False
ENABLE_MONGODB_CHECK = False
ENABLE_DJANGO_CACHE_CHECK = False

# Service-specific settings
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

ELASTICSEARCH_HOST = 'http://localhost:9200'

RABBITMQ_HOST = 'localhost'

CELERY_BROKER_URL = 'redis://localhost:6379/0'

MONGODB_URI = 'mongodb://localhost:27017'

# Custom URLs to monitor
CUSTOM_URLS_TO_CHECK = [
    'http://example-microservice-1.local/health',
    'http://example-microservice-2.local/health',
]
```

## Run the Server
Start your Django development server to test the installation:

```bash
python manage.py runserver
```

Verify the endpoints:
- Health: `http://127.0.0.1:8000/monitoring/health/`
- Metrics: `http://127.0.0.1:8000/monitoring/metrics/`

## Troubleshooting
- Ensure all required services (e.g., Redis, MongoDB) are running if their checks are enabled.
- Check your Django logs for any configuration errors.