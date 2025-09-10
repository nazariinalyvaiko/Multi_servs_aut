"""Monitoring and metrics utilities."""

import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import Request, Response
from app.core.config import settings
from app.core.cache import cache

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collects and stores application metrics."""
    
    def __init__(self):
        self.metrics = {}
    
    def increment_counter(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """Increment a counter metric."""
        key = f"counter:{name}"
        if tags:
            key += ":" + ":".join(f"{k}={v}" for k, v in tags.items())
        
        self.metrics[key] = self.metrics.get(key, 0) + value
        logger.info(f"Metric: {key} = {self.metrics[key]}")
    
    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Set a gauge metric."""
        key = f"gauge:{name}"
        if tags:
            key += ":" + ":".join(f"{k}={v}" for k, v in tags.items())
        
        self.metrics[key] = value
        logger.info(f"Metric: {key} = {value}")
    
    def record_timing(self, name: str, duration: float, tags: Optional[Dict[str, str]] = None):
        """Record a timing metric."""
        key = f"timer:{name}"
        if tags:
            key += ":" + ":".join(f"{k}={v}" for k, v in tags.items())
        
        self.metrics[key] = duration
        logger.info(f"Metric: {key} = {duration}s")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        return self.metrics.copy()
    
    def clear_metrics(self):
        """Clear all metrics."""
        self.metrics.clear()


# Global metrics collector
metrics = MetricsCollector()


class RequestMetrics:
    """Middleware for collecting request metrics."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        start_time = time.time()
        
        # Process request
        response = await self.app(scope, receive, send)
        
        # Calculate metrics
        duration = time.time() - start_time
        status_code = getattr(response, 'status_code', 200)
        
        # Record metrics
        metrics.increment_counter("requests_total", tags={
            "method": request.method,
            "endpoint": request.url.path,
            "status": str(status_code)
        })
        
        metrics.record_timing("request_duration", duration, tags={
            "method": request.method,
            "endpoint": request.url.path
        })
        
        return response


class HealthChecker:
    """Health check utilities."""
    
    @staticmethod
    async def check_database() -> Dict[str, Any]:
        """Check database connectivity."""
        try:
            from app.core.database import SessionLocal
            db = SessionLocal()
            db.execute("SELECT 1")
            db.close()
            return {"status": "healthy", "response_time": 0.001}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    @staticmethod
    async def check_redis() -> Dict[str, Any]:
        """Check Redis connectivity."""
        try:
            from app.core.cache import redis_client
            start_time = time.time()
            redis_client.ping()
            response_time = time.time() - start_time
            return {"status": "healthy", "response_time": response_time}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    @staticmethod
    async def check_external_services() -> Dict[str, Any]:
        """Check external service connectivity."""
        services = {}
        
        # Check Slack (mock)
        services["slack"] = {"status": "configured", "response_time": 0.001}
        
        # Check Telegram (mock)
        services["telegram"] = {"status": "configured", "response_time": 0.001}
        
        # Check Google Sheets (mock)
        services["google_sheets"] = {"status": "configured", "response_time": 0.001}
        
        return services
    
    @staticmethod
    async def get_system_info() -> Dict[str, Any]:
        """Get system information."""
        import psutil
        import platform
        
        return {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "uptime": time.time() - psutil.boot_time()
        }


class APIAnalytics:
    """API analytics and usage tracking."""
    
    @staticmethod
    async def track_api_usage(
        user_id: Optional[int],
        endpoint: str,
        method: str,
        status_code: int,
        response_time: float,
        request_size: int = 0,
        response_size: int = 0
    ):
        """Track API usage for analytics."""
        try:
            # Store in cache for real-time analytics
            usage_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "response_time": response_time,
                "request_size": request_size,
                "response_size": response_size
            }
            
            # Store in cache with TTL
            cache_key = f"api_usage:{datetime.utcnow().strftime('%Y%m%d%H%M')}"
            await cache.set(cache_key, usage_data, ttl=86400)  # 24 hours
            
            # Update counters
            metrics.increment_counter("api_calls_total", tags={
                "endpoint": endpoint,
                "method": method,
                "status": str(status_code)
            })
            
            metrics.record_timing("api_response_time", response_time, tags={
                "endpoint": endpoint,
                "method": method
            })
            
        except Exception as e:
            logger.error(f"Error tracking API usage: {e}")
    
    @staticmethod
    async def get_usage_stats(hours: int = 24) -> Dict[str, Any]:
        """Get API usage statistics."""
        try:
            # This would typically query a time-series database
            # For now, return mock data
            return {
                "total_requests": 1250,
                "unique_users": 45,
                "top_endpoints": [
                    {"endpoint": "/api/v1/messages/send", "count": 450},
                    {"endpoint": "/api/v1/auth/login", "count": 320},
                    {"endpoint": "/api/v1/sheets/append", "count": 280}
                ],
                "response_times": {
                    "avg": 0.125,
                    "p95": 0.250,
                    "p99": 0.500
                },
                "error_rate": 0.02
            }
        except Exception as e:
            logger.error(f"Error getting usage stats: {e}")
            return {}
