from app.core.config import settings
import redis.asyncio as redis

redis_client: redis.Redis | None = None

async def init_redis():
    global redis_client
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True
    )

async def close_redis():
    await redis_client.close()
    
def get_redis_client() -> redis.Redis:
    if redis_client is None:
        raise Exception("Redis client not initialized")
    return redis_client
