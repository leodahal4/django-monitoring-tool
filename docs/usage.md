# Usage

This document explains how to use the `django-health-metrics` app once installed in your Django project.

## Endpoints
The app provides two main endpoints under the configured URL prefix (e.g., `/monitoring/`):

### 1. Health Endpoint (`/monitoring/health/`)
- **Purpose**: Returns a JSON response with the status of configured health checks.
- **Access**: `GET http://127.0.0.1:8000/monitoring/health/`
- **Example Response**:
  ```json
  {
      "redis": {"status": "healthy", "response_time_ms": 10},
      "database": {"status": "healthy", "response_time_ms": 15},
      "memory": {"total": 16777216, "available": 8388608, "percent": 50},
      "cpu": {"cpu_percent": 20},
      "threads": {"total_threads": 10}
  }
  ```
- **Details**: Only enabled checks (via settings like `ENABLE_REDIS_CHECK`) appear in the response.

### 2. Metrics Endpoint (`/monitoring/metrics/`)
- **Purpose**: Exposes Prometheus-compatible metrics for monitoring.
- **Access**: `GET http://127.0.0.1:8000/monitoring/metrics/`
- **Example Output**:
  ```
  # HELP python_gc_objects_collected_total Objects collected during gc
  # TYPE python_gc_objects_collected_total counter
  python_gc_objects_collected_total{generation="0"} 123.0
  ```
- **Integration**: Use with Prometheus and Grafana for monitoring dashboards.

## Customizing Health Checks
- Enable/disable checks via settings (see `installation.md`).
- Add custom URLs to monitor by setting `CUSTOM_URLS_TO_CHECK` in `settings.py`.

## Example Usage
1. **Check Health**:
   ```bash
   curl http://127.0.0.1:8000/monitoring/health/
   ```
2. **Scrape Metrics**:
   ```bash
   curl http://127.0.0.1:8000/monitoring/metrics/
   ```

## Notes
- Health checks are dynamic and depend on your configuration.
- Metrics are generated using `prometheus-client` and include Python runtime metrics by default.