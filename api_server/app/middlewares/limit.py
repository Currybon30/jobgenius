import logging

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
    usage = await redis_client.get(usage_key)

    if usage is not None:
        await redis_client.incr(usage_key)
        await redis_client.expire(usage_key, MONTH_WINDOW)
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Usage key '{usage_key}' is not found in Redis"},
        )
