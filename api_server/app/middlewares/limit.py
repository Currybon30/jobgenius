import logging

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from app.db.redis import get_redis_client

logger = logging.getLogger(__name__)

RATE_LIMIT = 5  # Max requests per minute
RATE_WINDOW = 60  # 1 minute in seconds

MONTH_LIMIT = 5
MONTH_WINDOW = 30 * 24 * 60 * 60  # 30 days in seconds


async def increment_monthly_usage(anonymous_uuid: str):
    redis_client = get_redis_client()
    usage_key = f"usage:{anonymous_uuid}"
    count = await redis_client.incr(usage_key)
    if count == 1:
        await redis_client.expire(usage_key, MONTH_WINDOW)
    return count