from prometheus_client import generate_latest, REGISTRY, Counter, Histogram
from functools import lru_cache
from django.http import HttpResponse, JsonResponse
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from django.conf import settings
from django.db import connections
from django.core.cache import cache
import redis
import psutil
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Callable
import pika
import threading
from elasticsearch import Elasticsearch
from celery import Celery
import requests


logger = logging.getLogger(__name__)

# Constants
DEFAULT_TIMEOUT = getattr(settings, 'HEALTH_METRICS_DEFAULT_TIMEOUT', 2)
"""Default timeout for network operations in seconds."""
DEFAULT_THREADS_TIMEOUT = getattr(settings, 'HEALTH_METRICS_THREADS_TIMEOUT', 10)
"""Default timeout for thread-related operations in seconds."""
STATUS_HEALTHY = "healthy"
"""Status string for healthy services."""
STATUS_UNHEALTHY = "unhealthy"
"""Status string for unhealthy services."""
STATUS_NOT_CONNECTED = "not_connected"
"""Status string for services that are not connected."""

PROMETHEUS_HISOGRAM_ENABLED = getattr(settings, 'PROMETHEUS_HISOGRAM_ENABLED', False)
"""Flag to enable Prometheus histogram metrics."""
if PROMETHEUS_HISOGRAM_ENABLED:
    health_check_latency = Histogram(
        'health_check_latency_seconds',
        'Health check latency in seconds',
        ['service'],
        buckets=[0.01, 0.05, 0.1, 0.5, 1, 5, 10, 30]
    )
    health_check_counter = Counter(
        'health_check_latency_seconds',
        'Health check latency in seconds',
        ['service']
    )
"""Prometheus histogram metric for health check latency."""

CHECK_CONFIG = {
    "redis": {"enabled": "ENABLE_REDIS_CHECK", "requires": ["REDIS_HOST", "REDIS_PORT", "REDIS_DB"]},
    "database": {"enabled": "ENABLE_DB_CHECK", "requires": []},
    "cache": {"enabled": "ENABLE_CACHE_CHECK", "requires": []},
    "custom_urls": {"enabled": "CUSTOM_URLS_TO_CHECK", "requires": []},
    "rabbitmq": {"enabled": "ENABLE_RABBITMQ_CHECK", "requires": ["RABBITMQ_HOST"]},
    "elasticsearch": {"enabled": "ENABLE_ELASTICSEARCH_CHECK", "requires": ["ELASTICSEARCH_HOST"]},
    "celery": {"enabled": "ENABLE_CELERY_CHECK", "requires": ["CELERY_BROKER_URL"]},
}
"""Configuration for optional health checks with their enabling flags and required settings."""

class HealthChecker:
    """A class to manage and execute health checks for various services.

    Attributes:
        redis_client (redis.Redis): Reusable Redis client instance.
        es_client (Elasticsearch): Reusable Elasticsearch client instance.
        celery_app (Celery): Reusable Celery app instance.
    """

    def __init__(self):
        self.redis_client = None
        self.es_client = None
        self.celery_app = None
        self._requests_session = requests.Session()  # Reusable HTTP session for custom URLs
        retries = Retry(total=3, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
        self._requests_session.mount('http://', adapter)
        self._requests_session.mount('https://', adapter)

    def _get_redis_client(self) -> redis.Redis:
        """Lazily initialize and return a Redis client."""
        if not self.redis_client:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_timeout=DEFAULT_TIMEOUT
            )
        return self.redis_client

    def _get_es_client(self) -> Elasticsearch:
        """Lazily initialize and return an Elasticsearch client."""
        if not self.es_client:
            self.es_client = Elasticsearch([settings.ELASTICSEARCH_HOST], timeout=DEFAULT_TIMEOUT)
        return self.es_client

    def _get_celery_app(self) -> Celery:
        """Lazily initialize and return a Celery app."""
        if not self.celery_app:
            self.celery_app = Celery(broker=settings.CELERY_BROKER_URL)
        return self.celery_app

    def run_check(self, check_func: Callable, *args, **kwargs) -> Dict:
        """Execute a health check function and measure its response time.

        Args:
            check_func: The health check function to execute.
            *args: Positional arguments for the check function.
            **kwargs: Keyword arguments for the check function.

        Returns:
            Dict containing the check result with response time in milliseconds.
        """
        service_name = check_func.__name__.replace("check_", "")
        try:
            start = time.perf_counter()  # Higher precision than time.time()
            result = check_func(*args, **kwargs)
            response_time = (time.perf_counter() - start) * 1000
            if PROMETHEUS_HISOGRAM_ENABLED:
                health_check_latency.labels(service=service_name).observe(response_time)
                health_check_counter.labels(service=service_name, status="healthy").inc()
            return {"status": STATUS_HEALTHY, "response_time_ms": response_time, **(result or {})}
        except Exception as e:
            logger.error(f"Error in {check_func.__name__}: {e}")
            return {"status": STATUS_UNHEALTHY, "message": str(e), "response_time_ms": 0}

    @lru_cache(maxsize=None)
    def _is_configured(self, check_name: str) -> bool:
        """Check if a service is configured and enabled.

        Args:
            check_name: The name of the check (e.g., 'redis', 'database').

        Returns:
            True if the service is enabled and all required settings are present, False otherwise.
        """
        config = CHECK_CONFIG.get(check_name, {})
        enabled = getattr(settings, config.get("enabled", ""), False)
        if not enabled:
            return False
        return all(hasattr(settings, req) for req in config.get("requires", []))

    def check_redis(self) -> Dict:
        """Check Redis connectivity."""
        if not self._is_configured("redis"):
            return {"status": "not_connected"}
        self._get_redis_client().ping()
        return {}

    def check_database(self) -> Dict:
        """Check database connectivity."""
        if not self._is_configured("database"):
            return {"status": "not_connected"}
        connections['default'].cursor()
        return {}

    def check_cache(self) -> Dict:
        """Check cache read/write functionality."""
        if not self._is_configured("cache"):
            return {"status": "not_connected"}
        cache.set('health_check', 'ok', timeout=1)
        return {} if cache.get('health_check') == 'ok' else {"message": "Cache read/write failed"}

    def check_custom_urls(self) -> Dict:
        """Check the health of custom URLs in parallel."""
        urls = getattr(settings, 'CUSTOM_URLS_TO_CHECK', [])
        if not urls:
            return {"status": "None Provided"}
        
        results = {}
        with ThreadPoolExecutor(max_workers=min(len(urls), 5)) as executor:
            future_to_url = {
                executor.submit(self._requests_session.get, url, timeout=DEFAULT_TIMEOUT): url
                for url in urls
            }
            for future in future_to_url:
                url = future_to_url[future]
                try:
                    response = future.result()
                    results[url] = {} if response.status_code == 200 else {
                        "message": f"HTTP {response.status_code}"
                    }
                except Exception as e:
                    results[url] = {"message": str(e)}
        return {"urls": results}

    def check_memory(self) -> Dict:
        """Check system memory usage."""
        memory = psutil.virtual_memory()
        return {"total": memory.total, "available": memory.available, "percent": memory.percent}

    def check_cpu(self) -> Dict:
        """Check CPU usage."""
        return {"cpu_percent": psutil.cpu_percent(interval=0.1)}  # Reduced interval for faster response

    def check_threads(self) -> Dict:
        """Check active thread count."""
        return {"total_threads": threading.active_count()}

    def check_rabbitmq(self) -> Dict:
        """Check RabbitMQ connectivity."""
        if not self._is_configured("rabbitmq"):
            return {"status": "not_connected"}
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=settings.RABBITMQ_HOST, socket_timeout=DEFAULT_TIMEOUT)
        )
        connection.close()
        return {}

    def check_elasticsearch(self) -> Dict:
        """Check Elasticsearch connectivity."""
        if not self._is_configured("elasticsearch"):
            return {"status": "not_connected"}
        return {} if self._get_es_client().ping() else {"message": "Elasticsearch ping failed"}

    def check_celery(self) -> Dict:
        """Check Celery worker availability."""
        if not self._is_configured("celery"):
            return {"status": "not_connected"}
        result = self._get_celery_app().control.ping(timeout=DEFAULT_TIMEOUT)
        return {} if result else {"message": "No workers responded"}

checker = HealthChecker()

def metrics_view(request):
    """Expose Prometheus metrics.

    Args:
        request: The Django HTTP request object.

    Returns:
        HttpResponse with Prometheus metrics in text/plain format.
    """
    return HttpResponse(generate_latest(REGISTRY), content_type='text/plain')

def health_view(request):
    """Perform health checks on configured services and return their status.

    Args:
        request: The Django HTTP request object.

    Returns:
        JsonResponse containing the health status of all services.
    """
    checks = {
        "redis": checker.check_redis,
        "database": checker.check_database,
        "cache": checker.check_cache,
        "custom_urls": checker.check_custom_urls,
        "memory": checker.check_memory,
        "cpu": checker.check_cpu,
        "threads": checker.check_threads,
        "rabbitmq": checker.check_rabbitmq,
        "elasticsearch": checker.check_elasticsearch,
        "celery": checker.check_celery,
    }

    results = {}
    with ThreadPoolExecutor(max_workers=min(len(checks), 10)) as executor:
        future_to_check = {executor.submit(checker.run_check, func): name for name, func in checks.items()}
        for future in future_to_check:
            try:
                name = future_to_check[future]
                result = future.result(timeout=DEFAULT_THREADS_TIMEOUT)
                results[name] = result if result["status"] == STATUS_NOT_CONNECTED else {
                    "status": STATUS_HEALTHY if result.get("status") != STATUS_UNHEALTHY else STATUS_UNHEALTHY,
                    **result
                }
            except Exception as e:
                logger.error(f"Error in health check: {e}")
                results[name] = {"status": STATUS_UNHEALTHY, "message": str(e), "response_time_ms": 0}

    return JsonResponse(results)