import logging
import uuid

from app.auth.jwt_handler import decode_jwt
from app.db.redis import get_redis_client
from fastapi import HTTPException, Request

logger = logging.getLogger(__name__)

RATE_LIMIT = 5  # Max requests per minute
RATE_WINDOW = 60  # 1 minute in seconds

MONTH_LIMIT = 5
MONTH_WINDOW = 30 * 24 * 60 * 60  # 30 days in seconds


async def rate_limit_middleware(request: Request, call_next):
    if (request.url.path.startswith("/internal/")) or (request.url.path == "/health"):
        return await call_next(request)

    redis_client = get_redis_client()

    access_token = request.cookies.get("access_token")

    if access_token:
        try:
            payload = decode_jwt(access_token)
            if payload.get("user_id") is not None:
                return await call_next(request)
        except HTTPException:
            pass

    ip = request.headers.get("x-forwarded-for", request.client.host)
    ip = ip.split(",")[0].strip()
    anonymous_uuid = request.cookies.get("anonymous_uuid")

    # Convert to string anonymous_uuid
    anonymous_uuid = str(anonymous_uuid)

    # ---- 1. Rate limit (per minute) ----
    rate_key = f"rate:{anonymous_uuid + '_' + ip}"
    rate = await redis_client.get(rate_key)

    if rate is None:
        await redis_client.set(rate_key, 1, ex=RATE_WINDOW)
    elif int(rate) < RATE_LIMIT:
        await redis_client.incr(rate_key)
    else:
        logger.warning(f"Rate limit exceeded for IP: {ip}")
        raise HTTPException(
            status_code=429, detail="Too many requests. Please try again later.")

    # ---- 2. Monthly quota check (before request work) ----
    usage_key = f"usage:{anonymous_uuid}"
    usage = await redis_client.get(usage_key)

    if usage is None:
        await redis_client.set(usage_key, 1, ex=MONTH_WINDOW)
    else:
        if int(usage) >= MONTH_LIMIT:
            logger.warning(
                f"Monthly limit exceeded for Anonymous UUID: {anonymous_uuid}")
            raise HTTPException(
                status_code=403, detail="Monthly usage limit exceeded. Please log in to continue using our features.")
        await redis_client.incr(usage_key)

    response = await call_next(request)
    return response
