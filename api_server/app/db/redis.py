import logging
import redis.asyncio as redis
from app.core.config import settings

redis_client: redis.Redis | None = None

logger = logging.getLogger(__name__)

async def init_redis():
    global redis_client
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True
    )
    is_alive = await redis_client.ping()
    if not is_alive:
        raise RuntimeError("Failed to connect to Redis")
    logger.info("Redis client initialized and connected successfully")


async def close_redis():
    global redis_client
    if redis_client is not None:
        await redis_client.aclose()
        del redis_client
        logger.info("Redis client closed successfully")


def get_redis_client() -> redis.Redis:
    if redis_client is None:
        raise RuntimeError("Redis client not initialized")
    return redis_client
