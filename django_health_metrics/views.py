from prometheus_client import generate_latest, REGISTRY
from django.http import HttpResponse, JsonResponse
import redis
import time
import psutil
import threading
from django.conf import settings
from django.db import connections
from django.core.cache import cache

def metrics_view(request):
    return HttpResponse(generate_latest(REGISTRY), content_type='text/plain')

def check_redis():
    if not getattr(settings, 'ENABLE_REDIS_CHECK', False):
        return None
    try:
        start = time.time()
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB
        )
        r.ping()
        end = time.time()
        return {"status": "healthy", "response_time_ms": (end - start) * 1000}
    except redis.ConnectionError:
        return {"status": "unhealthy", "message": "Cannot connect to Redis"}

def check_database():
    if not getattr(settings, 'ENABLE_DB_CHECK', False):
        return None
    try:
        start = time.time()
        connections['default'].cursor()
        end = time.time()
        return {"status": "healthy", "response_time_ms": (end - start) * 1000}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}

def check_cache():
    if not getattr(settings, 'ENABLE_CACHE_CHECK', False):
        return None
    try:
        start = time.time()
        cache.set('health_check', 'ok', timeout=1)
        value = cache.get('health_check')
        end = time.time()
        if value == 'ok':
            return {"status": "healthy", "response_time_ms": (end - start) * 1000}
        else:
            return {"status": "unhealthy", "message": "Cache read/write failed"}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}

def check_elasticsearch():
    if not getattr(settings, 'ENABLE_ELASTICSEARCH_CHECK', False):
        return None
    try:
        from elasticsearch import Elasticsearch
        start = time.time()
        es = Elasticsearch(settings.ELASTICSEARCH_HOST)
        if es.ping():
            end = time.time()
            return {"status": "healthy", "response_time_ms": (end - start) * 1000}
        else:
            return {"status": "unhealthy", "message": "Elasticsearch ping failed"}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}

def check_rabbitmq():
    if not getattr(settings, 'ENABLE_RABBITMQ_CHECK', False):
        return None
    try:
        import pika
        start = time.time()
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST))
        connection.close()
        end = time.time()
        return {"status": "healthy", "response_time_ms": (end - start) * 1000}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}

def check_celery():
    if not getattr(settings, 'ENABLE_CELERY_CHECK', False):
        return None
    try:
        from celery import Celery
        start = time.time()
        app = Celery(broker=settings.CELERY_BROKER_URL)
        result = app.control.ping(timeout=1)
        end = time.time()
        if result:
            return {"status": "healthy", "response_time_ms": (end - start) * 1000}
        else:
            return {"status": "unhealthy", "message": "Celery workers not responding"}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}

def check_mongodb():
    if not getattr(settings, 'ENABLE_MONGODB_CHECK', False):
        return None
    try:
        from pymongo import MongoClient
        start = time.time()
        client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=1000)
        client.admin.command('ping')
        end = time.time()
        return {"status": "healthy", "response_time_ms": (end - start) * 1000}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}

def check_django_cache():
    if not getattr(settings, 'ENABLE_DJANGO_CACHE_CHECK', False):
        return None
    try:
        start = time.time()
        cache.set('django_cache_health_check', 'ok', timeout=1)
        value = cache.get('django_cache_health_check')
        end = time.time()
        if value == 'ok':
            return {"status": "healthy", "response_time_ms": (end - start) * 1000}
        else:
            return {"status": "unhealthy", "message": "Django cache read/write failed"}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}

def check_custom_urls():
    if not getattr(settings, 'CUSTOM_URLS_TO_CHECK', []):
        return None
    results = {}
    import requests
    for url in settings.CUSTOM_URLS_TO_CHECK:
        try:
            start = time.time()
            response = requests.get(url, timeout=2)
            end = time.time()
            if response.status_code == 200:
                results[url] = {"status": "healthy", "response_time_ms": (end - start) * 1000}
            else:
                results[url] = {"status": "unhealthy", "message": f"HTTP {response.status_code}"}
        except Exception as e:
            results[url] = {"status": "unhealthy", "message": str(e)}
    return results

def check_memory():
    memory = psutil.virtual_memory()
    return {"total": memory.total, "available": memory.available, "percent": memory.percent}

def check_cpu():
    return {"cpu_percent": psutil.cpu_percent(interval=1)}

def check_threads():
    return {"total_threads": threading.active_count()}

def health_view(request):
    health_checks = {}

    redis_check = check_redis()
    if redis_check:
        health_checks["redis"] = redis_check

    db_check = check_database()
    if db_check:
        health_checks["database"] = db_check

    cache_check = check_cache()
    if cache_check:
        health_checks["cache"] = cache_check

    elasticsearch_check = check_elasticsearch()
    if elasticsearch_check:
        health_checks["elasticsearch"] = elasticsearch_check

    rabbitmq_check = check_rabbitmq()
    if rabbitmq_check:
        health_checks["rabbitmq"] = rabbitmq_check

    celery_check = check_celery()
    if celery_check:
        health_checks["celery"] = celery_check

    mongodb_check = check_mongodb()
    if mongodb_check:
        health_checks["mongodb"] = mongodb_check

    django_cache_check = check_django_cache()
    if django_cache_check:
        health_checks["django_cache"] = django_cache_check

    custom_urls_check = check_custom_urls()
    if custom_urls_check:
        health_checks["custom_urls"] = custom_urls_check

    health_checks["memory"] = check_memory()
    health_checks["cpu"] = check_cpu()
    health_checks["threads"] = check_threads()

    return JsonResponse(health_checks)
