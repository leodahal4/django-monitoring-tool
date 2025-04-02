# Django Health Metrics

Django Health Metrics is a Django app that provides `/metrics` and `/health` endpoints for monitoring and health checks.

## Features
- `/metrics`: Exposes Prometheus metrics.
- `/health`: Provides dynamic health checks for Redis, database, memory, CPU, threads, Elasticsearch, RabbitMQ, Celery, MongoDB, Django cache, and custom URLs.

## Installation
1. Install the package via pip:
   ```bash
   pip install django-health-metrics
   ```

2. Add `health` to your `INSTALLED_APPS` in `settings.py`:
   ```python
   INSTALLED_APPS = [
       # ...existing apps...
       'django_health_metrics',
   ]
   ```

3. Include the health metrics URLs in your project's `urls.py`:
   ```python
   from django.urls import path, include

   urlpatterns = [
       # ...existing URLs...
       path('health-metrics/', include('django_health_metrics.urls')),
   ]
   ```

4. Configure settings as needed:
   ```python
   ENABLE_REDIS_CHECK = True
   ENABLE_DB_CHECK = True
   ENABLE_CACHE_CHECK = False
   ENABLE_ELASTICSEARCH_CHECK = True
   ENABLE_RABBITMQ_CHECK = True
   ENABLE_CELERY_CHECK = True
   ENABLE_MONGODB_CHECK = True
   ENABLE_DJANGO_CACHE_CHECK = True

   REDIS_HOST = 'localhost'
   REDIS_PORT = 6379
   REDIS_DB = 0

   ELASTICSEARCH_HOST = 'http://localhost:9200'

   RABBITMQ_HOST = 'localhost'

   CELERY_BROKER_URL = 'redis://localhost:6379/0'

   MONGODB_URI = 'mongodb://localhost:27017'

   CUSTOM_URLS_TO_CHECK = [
       'http://example-microservice-1.local/health',
       'http://example-microservice-2.local/health'
   ]
   ```

5. Run the server:
   ```bash
   python manage.py runserver
   ```

## Usage
Once installed and configured, you can use the following endpoints:

- **Health Check Endpoint**: Access the `/health-metrics/health` endpoint to get a JSON response with the status of various health checks (Redis, database, memory, CPU, threads, Elasticsearch, RabbitMQ, Celery, MongoDB, Django cache, and custom URLs). Example:
  ```bash
  curl http://127.0.0.1:8000/health-metrics/health/
  ```

  Example response:
  ```json
  {
      "redis": {"status": "healthy", "response_time_ms": 10},
      "database": {"status": "healthy", "response_time_ms": 15},
      "cache": {"status": "healthy", "response_time_ms": 5},
      "elasticsearch": {"status": "healthy", "response_time_ms": 20},
      "rabbitmq": {"status": "healthy", "response_time_ms": 25},
      "celery": {"status": "healthy", "response_time_ms": 30},
      "mongodb": {"status": "healthy", "response_time_ms": 35},
      "django_cache": {"status": "healthy", "response_time_ms": 10},
      "custom_urls": {
          "http://example-microservice-1.local/health": {"status": "healthy", "response_time_ms": 50},
          "http://example-microservice-2.local/health": {"status": "unhealthy", "message": "Timeout"}
      },
      "memory": {"total": 16777216, "available": 8388608, "percent": 50},
      "cpu": {"cpu_percent": 20},
      "threads": {"total_threads": 10}
  }
  ```

- **Metrics Endpoint**: Access the `/metrics` endpoint to expose Prometheus metrics for monitoring. Example:
  ```bash
  curl http://127.0.0.1:8000/health-metrics/metrics/
  ```

  This will return Prometheus-compatible metrics for integration with monitoring tools.

## Contributing
1. Fork the repository.
2. Create a new branch: `git checkout -b feature-name`.
3. Make your changes and write tests.
4. Run tests: `pytest`.
5. Submit a pull request.

## Development Setup
1. Clone the repo: `git clone https://github.com/leodahal4/django-health-metrics.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the example project: `cd example && python manage.py runserver`


## License
This project is licensed under the MIT License.