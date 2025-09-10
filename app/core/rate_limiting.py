"""Rate limiting utilities using Redis."""

import time
from typing import Optional
from fastapi import HTTPException, Request, status
from app.core.config import settings
import redis

# Redis connection for rate limiting
redis_client = redis.from_url(settings.redis_url, decode_responses=True)

class RateLimiter:
    """Rate limiter using Redis sliding window algorithm."""
    
    def __init__(self, redis_client=redis_client):
        self.redis = redis_client
    
    async def is_allowed(
        self, 
        key: str, 
        limit: int, 
        window: int,
        identifier: Optional[str] = None
    ) -> bool:
        """
        Check if request is allowed based on rate limit.
        
        Args:
            key: Rate limit key (e.g., 'api:user:123')
            limit: Maximum number of requests
            window: Time window in seconds
            identifier: Optional identifier for logging
            
        Returns:
            True if request is allowed, False otherwise
        """
        try:
            current_time = int(time.time())
            window_start = current_time - window
            
            # Use Redis pipeline for atomic operations
            pipe = self.redis.pipeline()
            
            # Remove expired entries
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(current_time): current_time})
            
            # Set expiration
            pipe.expire(key, window)
            
            results = pipe.execute()
            current_count = results[1]
            
            return current_count < limit
            
        except Exception as e:
            # If Redis is down, allow the request (fail open)
            print(f"Rate limiting error: {e}")
            return True
    
    async def get_remaining_requests(
        self, 
        key: str, 
        limit: int, 
        window: int
    ) -> int:
        """Get remaining requests for the current window."""
        try:
            current_time = int(time.time())
            window_start = current_time - window
            
            # Remove expired entries
            self.redis.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            current_count = self.redis.zcard(key)
            
            return max(0, limit - current_count)
            
        except Exception:
            return limit


def get_rate_limit_key(request: Request, user_id: Optional[int] = None) -> str:
    """Generate rate limit key based on request and user."""
    if user_id:
        return f"rate_limit:user:{user_id}"
    else:
        # Use IP address for anonymous users
        client_ip = request.client.host
        return f"rate_limit:ip:{client_ip}"


# Rate limit decorator
def rate_limit(limit: int, window: int = 60):
    """Decorator for rate limiting endpoints."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request from kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                return await func(*args, **kwargs)
            
            # Get user ID if available
            user_id = getattr(request.state, 'user_id', None)
            
            # Generate rate limit key
            key = get_rate_limit_key(request, user_id)
            
            # Check rate limit
            limiter = RateLimiter()
            is_allowed = await limiter.is_allowed(key, limit, window)
            
            if not is_allowed:
                remaining = await limiter.get_remaining_requests(key, limit, window)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded",
                        "limit": limit,
                        "window": window,
                        "remaining": remaining,
                        "retry_after": window
                    },
                    headers={
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": str(remaining),
                        "X-RateLimit-Reset": str(int(time.time()) + window),
                        "Retry-After": str(window)
                    }
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
