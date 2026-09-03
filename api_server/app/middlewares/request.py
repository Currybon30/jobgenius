import logging
import time

from starlette.datastructures import MutableHeaders
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.auth.jwt_handler import decode_jwt
from app.db.redis import get_redis_client
from app.middlewares.limit import MONTH_LIMIT, RATE_LIMIT, RATE_WINDOW

logger = logging.getLogger(__name__)


class RequestMiddleware:
    """Single ASGI middleware: logging, rate limit, and process-time header."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        start = time.time()
        logger.info("%s %s", request.method, request.url)

        blocked = await self._maybe_block(request)
        if blocked is not None:
            logger.info("Status: %s", blocked.status_code)
            await blocked(scope, receive, send)
            return

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["X-Process-Time"] = f"{time.time() - start:.4f}"
                logger.info("Status: %s", message.get("status"))
                logger.info(
                    "Processed %s %s in %.4f seconds",
                    request.method,
                    request.url,
                    time.time() - start,
                )
            await send(message)

        await self.app(scope, receive, send_wrapper)

    async def _maybe_block(self, request: Request) -> JSONResponse | None:
        if request.url.path.startswith("/internal/") or request.url.path == "/health":
            return None

        redis_client = get_redis_client()
        access_token = request.cookies.get("access_token")
        if access_token:
            try:
                payload = decode_jwt(access_token)
                if payload.get("user_id") is not None:
                    return None
            except Exception:
                pass

        ip = request.headers.get("x-forwarded-for") or (
            request.client.host if request.client else ""
        )
        ip = ip.split(",")[0].strip()
        anonymous_uuid = str(request.cookies.get("anonymous_uuid"))

        rate_key = f"rate:{anonymous_uuid}_{ip}"
        rate = await redis_client.get(rate_key)
        if rate is None:
            await redis_client.set(rate_key, 1, ex=RATE_WINDOW)
        elif int(rate) < RATE_LIMIT:
            await redis_client.incr(rate_key)
        else:
            logger.warning(
                "Rate limit exceeded for anonymous UUID: %s on IP: %s",
                anonymous_uuid,
                ip,
            )
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."},
            )

        if request.url.path.startswith("/api/recommendations"):
            return None

        usage_key = f"usage:{anonymous_uuid}"
        usage = await redis_client.get(usage_key)
        if usage is None:
            await redis_client.set(usage_key, 0)
        elif int(usage) >= MONTH_LIMIT:
            logger.warning(
                "Monthly limit exceeded for Anonymous UUID: %s", anonymous_uuid
            )
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "Monthly usage limit exceeded. Please log in to continue using our features."
                },
            )
        return None
