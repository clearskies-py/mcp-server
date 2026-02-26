"""
Observability concept explanations for clearskies framework.

This module contains explanations for logging, caching, and production monitoring.
"""

import textwrap

OBSERVABILITY_CONCEPTS = {
    "logging": textwrap.dedent("""\
        # Logging & Observability in clearskies

        clearskies integrates with Python's standard logging infrastructure and supports
        various observability patterns for production monitoring.

        ## Python Logging Integration

        clearskies uses Python's standard logging module. Configure logging at application startup:

        ```python
        import logging
        import clearskies

        # Basic logging configuration
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Get the clearskies logger
        logger = logging.getLogger('clearskies')
        logger.setLevel(logging.DEBUG)  # Enable debug logging for clearskies
        ```

        ## Structured Logging with structlog

        For production applications, structured logging is recommended:

        ```python
        import structlog
        import logging

        # Configure structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        logger = structlog.get_logger()
        ```

        ## Request/Response Logging

        Log requests and responses in your endpoints:

        ```python
        import clearskies
        import logging

        logger = logging.getLogger(__name__)

        class LoggingMixin:
            def pre_save(self, data):
                logger.info("Creating/updating record", extra={"data": data})
                return data

            def save_finished(self):
                logger.info("Record saved", extra={"id": self.id})

        class User(LoggingMixin, clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()
            id = clearskies.columns.Uuid()
            name = clearskies.columns.String()
        ```

        ## Custom Logging in Callable Endpoints

        ```python
        import clearskies
        import logging

        logger = logging.getLogger(__name__)

        def my_endpoint(request_data: dict):
            logger.info("Processing request", extra={
                "action": "my_endpoint",
                "input_keys": list(request_data.keys()),
            })

            try:
                result = process_data(request_data)
                logger.info("Request processed successfully", extra={
                    "action": "my_endpoint",
                    "result_count": len(result),
                })
                return {"status": "success", "data": result}
            except Exception as e:
                logger.error("Request failed", extra={
                    "action": "my_endpoint",
                    "error": str(e),
                }, exc_info=True)
                raise

        cli = clearskies.contexts.Cli(
            clearskies.endpoints.Callable(
                callable=my_endpoint,
                input_requirements={"request_data": dict},
            )
        )
        ```

        ## Error Tracking

        Integrate with error tracking services:

        ```python
        import sentry_sdk
        import clearskies
        import os

        # Initialize Sentry
        sentry_sdk.init(
            dsn=os.environ.get("SENTRY_DSN"),
            environment=os.environ.get("ENVIRONMENT", "development"),
            traces_sample_rate=0.1,
        )

        # Errors in clearskies will automatically be captured by Sentry
        ```

        ## Metrics Collection

        Collect metrics using Prometheus or similar:

        ```python
        from prometheus_client import Counter, Histogram, start_http_server
        import clearskies
        import time

        # Define metrics
        REQUEST_COUNT = Counter(
            'clearskies_requests_total',
            'Total requests',
            ['endpoint', 'method', 'status']
        )
        REQUEST_LATENCY = Histogram(
            'clearskies_request_latency_seconds',
            'Request latency',
            ['endpoint']
        )

        class MetricsMiddleware:
            def __init__(self, endpoint_name):
                self.endpoint_name = endpoint_name

            def __call__(self, func):
                def wrapper(*args, **kwargs):
                    start_time = time.time()
                    try:
                        result = func(*args, **kwargs)
                        REQUEST_COUNT.labels(
                            endpoint=self.endpoint_name,
                            method='POST',
                            status='success'
                        ).inc()
                        return result
                    except Exception as e:
                        REQUEST_COUNT.labels(
                            endpoint=self.endpoint_name,
                            method='POST',
                            status='error'
                        ).inc()
                        raise
                    finally:
                        REQUEST_LATENCY.labels(
                            endpoint=self.endpoint_name
                        ).observe(time.time() - start_time)
                return wrapper

        # Start metrics server
        start_http_server(8000)
        ```

        ## OpenTelemetry Integration

        For distributed tracing:

        ```python
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

        # Configure OpenTelemetry
        trace.set_tracer_provider(TracerProvider())
        tracer = trace.get_tracer(__name__)

        otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317")
        span_processor = BatchSpanProcessor(otlp_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)

        # Use in your code
        def my_function():
            with tracer.start_as_current_span("my_operation") as span:
                span.set_attribute("custom.attribute", "value")
                # Your code here
                return result
        ```

        ## Health Check Endpoints

        clearskies provides a built-in health check endpoint:

        ```python
        import clearskies

        health_check = clearskies.endpoints.HealthCheck()

        # Or with custom checks
        def custom_health_check():
            # Check database connection
            # Check external services
            return {"status": "healthy", "checks": {"db": "ok", "cache": "ok"}}

        wsgi = clearskies.contexts.WsgiRef(
            clearskies.endpoints.EndpointGroup(
                endpoints=[
                    clearskies.endpoints.HealthCheck(url="health"),
                    clearskies.endpoints.Callable(
                        url="health/detailed",
                        callable=custom_health_check,
                    ),
                ]
            )
        )
        ```

        ## Best Practices

        1. **Use structured logging** – JSON format for easy parsing
        2. **Include correlation IDs** – Track requests across services
        3. **Log at appropriate levels** – DEBUG for development, INFO/WARN for production
        4. **Don't log sensitive data** – Mask passwords, tokens, PII
        5. **Set up alerting** – Alert on error rates, latency spikes
        6. **Use sampling for traces** – Don't trace every request in production
        7. **Monitor resource usage** – CPU, memory, connections
        8. **Implement health checks** – For load balancer integration

        ## Log Levels Guide

        | Level | Use Case |
        |-------|----------|
        | DEBUG | Detailed debugging information |
        | INFO | General operational events |
        | WARNING | Unexpected but handled situations |
        | ERROR | Errors that need attention |
        | CRITICAL | System-level failures |
    """),
    "caching": textwrap.dedent("""\
        # Caching in clearskies

        While clearskies doesn't provide built-in caching, it integrates well with
        Python caching libraries and patterns. This guide covers common caching
        strategies for clearskies applications.

        ## In-Memory Caching with functools

        For simple function-level caching:

        ```python
        from functools import lru_cache
        import clearskies

        @lru_cache(maxsize=100)
        def get_expensive_data(key: str) -> dict:
            # Expensive computation or external API call
            return {"key": key, "data": "..."}

        def my_endpoint(key: str):
            return get_expensive_data(key)
        ```

        ## Redis Caching

        For distributed caching across multiple instances:

        ```python
        import redis
        import json
        import clearskies
        import os
        from functools import wraps

        # Redis connection
        redis_client = redis.Redis(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=int(os.environ.get("REDIS_PORT", "6379")),
            db=0,
            decode_responses=True,
        )

        def cache_result(ttl_seconds: int = 300):
            \"\"\"Decorator to cache function results in Redis.\"\"\"
            def decorator(func):
                @wraps(func)
                def wrapper(*args, **kwargs):
                    # Create cache key from function name and arguments
                    cache_key = f"{func.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"

                    # Try to get from cache
                    cached = redis_client.get(cache_key)
                    if cached:
                        return json.loads(cached)

                    # Compute result
                    result = func(*args, **kwargs)

                    # Store in cache
                    redis_client.setex(cache_key, ttl_seconds, json.dumps(result))

                    return result
                return wrapper
            return decorator

        @cache_result(ttl_seconds=60)
        def get_user_stats(user_id: str) -> dict:
            # Expensive computation
            return {"user_id": user_id, "stats": "..."}
        ```

        ## Model-Level Caching

        Cache model queries:

        ```python
        import clearskies
        import redis
        import json

        redis_client = redis.Redis(host="localhost", decode_responses=True)

        class CachedUserMixin:
            @classmethod
            def get_cached(cls, user_id: str, ttl: int = 300):
                cache_key = f"user:{user_id}"

                # Try cache first
                cached = redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)

                # Query from backend
                users = cls()
                user = users.find(f"id={user_id}")
                if user.exists:
                    user_data = {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                    }
                    redis_client.setex(cache_key, ttl, json.dumps(user_data))
                    return user_data
                return None

            def invalidate_cache(self):
                cache_key = f"user:{self.id}"
                redis_client.delete(cache_key)

            def save_finished(self):
                # Invalidate cache on save
                self.invalidate_cache()

        class User(CachedUserMixin, clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()
            id = clearskies.columns.Uuid()
            name = clearskies.columns.String()
            email = clearskies.columns.Email()
        ```

        ## Query Result Caching

        Cache expensive query results:

        ```python
        import clearskies
        import hashlib
        import json

        class QueryCache:
            def __init__(self, redis_client, default_ttl: int = 300):
                self.redis = redis_client
                self.default_ttl = default_ttl

            def get_or_compute(self, cache_key: str, compute_func, ttl: int = None):
                ttl = ttl or self.default_ttl

                cached = self.redis.get(cache_key)
                if cached:
                    return json.loads(cached)

                result = compute_func()
                self.redis.setex(cache_key, ttl, json.dumps(result))
                return result

            def invalidate(self, pattern: str):
                for key in self.redis.scan_iter(pattern):
                    self.redis.delete(key)

        # Usage
        query_cache = QueryCache(redis_client)

        def get_active_users():
            def compute():
                users = User()
                return [
                    {"id": u.id, "name": u.name}
                    for u in users.where("status=active").limit(100)
                ]

            return query_cache.get_or_compute("active_users", compute, ttl=60)
        ```

        ## Response Caching

        Cache entire endpoint responses:

        ```python
        import clearskies
        import hashlib
        import json

        def cached_endpoint(ttl_seconds: int = 300):
            def decorator(func):
                def wrapper(*args, **kwargs):
                    # Create cache key from request
                    request_hash = hashlib.md5(
                        json.dumps(kwargs, sort_keys=True).encode()
                    ).hexdigest()
                    cache_key = f"response:{func.__name__}:{request_hash}"

                    cached = redis_client.get(cache_key)
                    if cached:
                        return json.loads(cached)

                    result = func(*args, **kwargs)
                    redis_client.setex(cache_key, ttl_seconds, json.dumps(result))
                    return result
                return wrapper
            return decorator

        @cached_endpoint(ttl_seconds=60)
        def list_products(category: str = None):
            products = Product()
            if category:
                products = products.where(f"category={category}")
            return [{"id": p.id, "name": p.name} for p in products.limit(50)]
        ```

        ## Cache Invalidation Strategies

        ### Time-Based (TTL)

        ```python
        # Set TTL when caching
        redis_client.setex("key", 300, "value")  # Expires in 5 minutes
        ```

        ### Event-Based

        ```python
        class User(clearskies.Model):
            def save_finished(self):
                # Invalidate user cache
                redis_client.delete(f"user:{self.id}")
                # Invalidate related caches
                redis_client.delete("active_users")
                redis_client.delete(f"user_stats:{self.id}")
        ```

        ### Pattern-Based

        ```python
        def invalidate_user_caches(user_id: str):
            # Delete all keys matching pattern
            for key in redis_client.scan_iter(f"*user*{user_id}*"):
                redis_client.delete(key)
        ```

        ## Cache-Aside Pattern

        The most common caching pattern:

        ```python
        def get_user(user_id: str):
            # 1. Check cache
            cached = cache.get(f"user:{user_id}")
            if cached:
                return cached

            # 2. Load from database
            users = User()
            user = users.find(f"id={user_id}")
            if not user.exists:
                return None

            # 3. Store in cache
            user_data = {"id": user.id, "name": user.name}
            cache.set(f"user:{user_id}", user_data, ttl=300)

            return user_data
        ```

        ## Best Practices

        1. **Choose appropriate TTLs** – Balance freshness vs. performance
        2. **Use cache prefixes** – Organize keys by type (user:, product:, etc.)
        3. **Implement cache warming** – Pre-populate cache on startup
        4. **Monitor cache hit rates** – Track effectiveness
        5. **Handle cache failures gracefully** – Fall back to database
        6. **Consider cache stampede** – Use locking for expensive computations
        7. **Don't cache sensitive data** – Or encrypt it
        8. **Set memory limits** – Prevent cache from growing unbounded

        ## Cache Stampede Prevention

        ```python
        import time
        import random

        def get_with_lock(cache_key: str, compute_func, ttl: int = 300):
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Try to acquire lock
            lock_key = f"lock:{cache_key}"
            lock_acquired = redis_client.set(lock_key, "1", nx=True, ex=10)

            if lock_acquired:
                try:
                    # Compute and cache
                    result = compute_func()
                    redis_client.setex(cache_key, ttl, json.dumps(result))
                    return result
                finally:
                    redis_client.delete(lock_key)
            else:
                # Wait and retry
                time.sleep(0.1 + random.random() * 0.1)
                return get_with_lock(cache_key, compute_func, ttl)
        ```
    """),
}
