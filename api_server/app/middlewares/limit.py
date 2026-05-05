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
    redis_client = get_redis_client()
    guest_id = request.cookies.get("guest_id") or str(uuid.uuid4())

    # ---- 1. Rate limit (per minute) ----
    rate_key = f"rate:{ip}"
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
    usage_key = f"usage:{guest_id}"
    usage = await redis_client.get(usage_key)

    if usage is None:
        await redis_client.set(usage_key, 1, ex=MONTH_WINDOW)
    else:
        if int(usage) >= MONTH_LIMIT:
            logger.warning(f"Monthly limit exceeded for Guest ID: {guest_id}")
            raise HTTPException(
                status_code=403, detail="Monthly usage limit exceeded. Please log in to continue using our features.")
        await redis_client.incr(usage_key)

    # --- 3. Process request and set guest cookie if needed ----
    response = await call_next(request)
    if "guest_id" not in request.cookies:
        response.set_cookie(
            # secure=True,  # TODO: Uncomment this when we have HTTPS
            key="guest_id",
            value=guest_id,
            max_age=MONTH_WINDOW,
            httponly=False,  # httponly is used to prevent frontend from accessing the cookie through document.cookie
            samesite="lax"
        )

    return response
