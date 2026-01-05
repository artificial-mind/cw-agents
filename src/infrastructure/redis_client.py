"""
Redis client for state management and caching.
No pub/sub - only used for state persistence and caching.
"""
import json
import logging
from typing import Optional, Any, Dict
from datetime import timedelta
import redis.asyncio as aioredis

from ..core.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Async Redis client for state and cache management.
    Does NOT use pub/sub (replaced by A2A protocol).
    """
    
    def __init__(self):
        self.client: Optional[aioredis.Redis] = None
        self.enabled = settings.REDIS_ENABLED
        
        if self.enabled:
            logger.info("Redis client initialized for state/cache management")
        else:
            logger.warning("Redis disabled - state/cache will be in-memory only")
    
    async def connect(self):
        """Establish Redis connection."""
        if not self.enabled:
            return
        
        try:
            self.client = await aioredis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
                password=settings.REDIS_PASSWORD,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Test connection
            await self.client.ping()
            logger.info(f"Connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.enabled = False
            raise
    
    async def close(self):
        """Close Redis connection."""
        if self.client:
            await self.client.aclose()
            logger.info("Redis connection closed")
    
    # State Management
    
    async def get_state(self, key: str) -> Optional[Dict[str, Any]]:
        """Get state from Redis."""
        if not self.enabled or not self.client:
            return None
        
        try:
            data = await self.client.get(f"state:{key}")
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Error getting state {key}: {e}")
            return None
    
    async def set_state(
        self,
        key: str,
        state: Dict[str, Any],
        ttl: Optional[int] = None
    ):
        """Set state in Redis."""
        if not self.enabled or not self.client:
            return
        
        try:
            data = json.dumps(state)
            if ttl:
                await self.client.setex(f"state:{key}", ttl, data)
            else:
                await self.client.set(f"state:{key}", data)
        except Exception as e:
            logger.error(f"Error setting state {key}: {e}")
    
    async def delete_state(self, key: str):
        """Delete state from Redis."""
        if not self.enabled or not self.client:
            return
        
        try:
            await self.client.delete(f"state:{key}")
        except Exception as e:
            logger.error(f"Error deleting state {key}: {e}")
    
    async def exists_state(self, key: str) -> bool:
        """Check if state exists."""
        if not self.enabled or not self.client:
            return False
        
        try:
            return bool(await self.client.exists(f"state:{key}"))
        except Exception as e:
            logger.error(f"Error checking state {key}: {e}")
            return False
    
    # Cache Management
    
    async def get_cache(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.enabled or not self.client:
            return None
        
        try:
            data = await self.client.get(f"cache:{key}")
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Error getting cache {key}: {e}")
            return None
    
    async def set_cache(
        self,
        key: str,
        value: Any,
        ttl: int = 3600
    ):
        """Set value in cache with TTL."""
        if not self.enabled or not self.client:
            return
        
        try:
            data = json.dumps(value)
            await self.client.setex(f"cache:{key}", ttl, data)
        except Exception as e:
            logger.error(f"Error setting cache {key}: {e}")
    
    async def delete_cache(self, key: str):
        """Delete value from cache."""
        if not self.enabled or not self.client:
            return
        
        try:
            await self.client.delete(f"cache:{key}")
        except Exception as e:
            logger.error(f"Error deleting cache {key}: {e}")
    
    async def clear_cache_pattern(self, pattern: str):
        """Clear all cache keys matching pattern."""
        if not self.enabled or not self.client:
            return
        
        try:
            keys = await self.client.keys(f"cache:{pattern}")
            if keys:
                await self.client.delete(*keys)
                logger.info(f"Cleared {len(keys)} cache keys matching {pattern}")
        except Exception as e:
            logger.error(f"Error clearing cache pattern {pattern}: {e}")
    
    # Crew State Management (for monitoring and batch operations)
    
    async def add_to_monitoring(self, crew_name: str, task_id: str, data: Dict[str, Any]):
        """Add task to monitoring set."""
        if not self.enabled or not self.client:
            return
        
        try:
            key = f"monitoring:{crew_name}"
            task_data = json.dumps({"task_id": task_id, **data})
            await self.client.sadd(key, task_data)
        except Exception as e:
            logger.error(f"Error adding to monitoring: {e}")
    
    async def remove_from_monitoring(self, crew_name: str, task_id: str):
        """Remove task from monitoring set."""
        if not self.enabled or not self.client:
            return
        
        try:
            key = f"monitoring:{crew_name}"
            # Get all members and find matching task_id
            members = await self.client.smembers(key)
            for member in members:
                data = json.loads(member)
                if data.get("task_id") == task_id:
                    await self.client.srem(key, member)
                    break
        except Exception as e:
            logger.error(f"Error removing from monitoring: {e}")
    
    async def get_monitoring_tasks(self, crew_name: str) -> list[Dict[str, Any]]:
        """Get all monitoring tasks for crew."""
        if not self.enabled or not self.client:
            return []
        
        try:
            key = f"monitoring:{crew_name}"
            members = await self.client.smembers(key)
            return [json.loads(member) for member in members]
        except Exception as e:
            logger.error(f"Error getting monitoring tasks: {e}")
            return []
    
    # Metrics
    
    async def increment_metric(self, key: str, amount: int = 1):
        """Increment metric counter."""
        if not self.enabled or not self.client:
            return
        
        try:
            await self.client.incrby(f"metric:{key}", amount)
        except Exception as e:
            logger.error(f"Error incrementing metric {key}: {e}")
    
    async def get_metric(self, key: str) -> int:
        """Get metric value."""
        if not self.enabled or not self.client:
            return 0
        
        try:
            value = await self.client.get(f"metric:{key}")
            return int(value) if value else 0
        except Exception as e:
            logger.error(f"Error getting metric {key}: {e}")
            return 0
    
    async def reset_metrics(self):
        """Reset all metrics."""
        if not self.enabled or not self.client:
            return
        
        try:
            keys = await self.client.keys("metric:*")
            if keys:
                await self.client.delete(*keys)
                logger.info(f"Reset {len(keys)} metrics")
        except Exception as e:
            logger.error(f"Error resetting metrics: {e}")
    
    # Health Check
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Redis health."""
        if not self.enabled:
            return {"status": "disabled"}
        
        if not self.client:
            return {"status": "disconnected"}
        
        try:
            await self.client.ping()
            info = await self.client.info("server")
            return {
                "status": "healthy",
                "redis_version": info.get("redis_version"),
                "uptime_seconds": info.get("uptime_in_seconds")
            }
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}


# Global client instance
_redis_client: Optional[RedisClient] = None


async def get_redis_client() -> RedisClient:
    """Get global Redis client."""
    global _redis_client
    
    if _redis_client is None:
        _redis_client = RedisClient()
        await _redis_client.connect()
    
    return _redis_client


async def close_redis_client():
    """Close global Redis client."""
    global _redis_client
    
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
