"""Caching utilities using Redis."""

import json
import pickle
from typing import Any, Optional, Union
from datetime import timedelta
from app.core.config import settings
import redis

# Redis connection for caching
redis_client = redis.from_url(settings.redis_url, decode_responses=False)

class CacheManager:
    """Redis-based cache manager with serialization support."""
    
    def __init__(self, redis_client=redis_client, default_ttl: int = 3600):
        self.redis = redis_client
        self.default_ttl = default_ttl
    
    async def get(
        self, 
        key: str, 
        deserialize: bool = True
    ) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            deserialize: Whether to deserialize the value
            
        Returns:
            Cached value or None if not found
        """
        try:
            value = self.redis.get(key)
            if value is None:
                return None
            
            if deserialize:
                try:
                    # Try JSON first
                    return json.loads(value.decode('utf-8'))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # Fall back to pickle
                    return pickle.loads(value)
            else:
                return value.decode('utf-8')
                
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        serialize: bool = True
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            serialize: Whether to serialize the value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if serialize:
                try:
                    # Try JSON first
                    serialized_value = json.dumps(value, default=str)
                except (TypeError, ValueError):
                    # Fall back to pickle
                    serialized_value = pickle.dumps(value)
            else:
                serialized_value = str(value).encode('utf-8')
            
            ttl = ttl or self.default_ttl
            return self.redis.setex(key, ttl, serialized_value)
            
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            return bool(self.redis.exists(key))
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache clear pattern error: {e}")
            return 0
    
    async def get_or_set(
        self, 
        key: str, 
        factory_func, 
        ttl: Optional[int] = None,
        *args, 
        **kwargs
    ) -> Any:
        """
        Get value from cache or set it using factory function.
        
        Args:
            key: Cache key
            factory_func: Function to call if value not in cache
            ttl: Time to live in seconds
            *args, **kwargs: Arguments for factory function
            
        Returns:
            Cached value or result from factory function
        """
        value = await self.get(key)
        if value is not None:
            return value
        
        # Value not in cache, generate it
        value = await factory_func(*args, **kwargs)
        await self.set(key, value, ttl)
        return value


# Global cache instance
cache = CacheManager()

# Cache decorator
def cache_result(ttl: int = 3600, key_prefix: str = ""):
    """Decorator to cache function results."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            result = await cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator
