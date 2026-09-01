import logging

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

    ip = request.headers.get("x-forwarded-for", request.client.host)  # type: ignore
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
        logger.warning(
            f"Rate limit exceeded for anonymous UUID: {anonymous_uuid} on IP: {ip}"
        )
        raise HTTPException(
            status_code=429, detail="Too many requests. Please try again later."
        )

    # ---- 2. Monthly quota check (before request work) ----
    usage_key = f"usage:{anonymous_uuid}"
    usage = await redis_client.get(usage_key)

    if request.url.path.startswith(
        "/api/recommendations"
    ):  # skip monthly quota check for recommendations
        return await call_next(request)

    if usage is None:
        await redis_client.set(usage_key, 0)
    else:
        if int(usage) >= MONTH_LIMIT:
            logger.warning(
                f"Monthly limit exceeded for Anonymous UUID: {anonymous_uuid}"
            )
            raise HTTPException(
                status_code=403,
                detail="Monthly usage limit exceeded. Please log in to continue using our features.",
            )

    response = await call_next(request)
    return response


async def increment_monthly_usage(anonymous_uuid: str):
    redis_client = get_redis_client()
    usage_key = f"usage:{anonymous_uuid}"
    usage = await redis_client.get(usage_key)

    if usage is not None:
        await redis_client.incr(usage_key)
        await redis_client.expire(usage_key, MONTH_WINDOW)
    else:
        raise KeyError(f"Usage key '{usage_key}' is not found in Redis")
