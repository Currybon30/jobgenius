import logging
import time

from app.auth.jwt_handler import decode_jwt
from app.db.redis import get_redis_client
from app.helpers.limit_helper import MONTH_LIMIT, MONTH_WINDOW, RATE_LIMIT, RATE_WINDOW
from fastapi import FastAPI, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)


class MyBaseHTTPMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        start = time.time()
        logger.info("[START] Request: %s %s", request.method, request.url)
        try:
            if (
                request.url.path.startswith("/internal/")
                or request.url.path == "/health"
            ):
                response = await call_next(request)
                logger.info("[STATUS CODE] Response: %s", response.status_code)
                return response
            redis_client = get_redis_client()
            access_token = request.cookies.get("access_token")
            if access_token:
                try:
                    payload = decode_jwt(access_token)
                    if payload.get("user_id") is not None:
                        response = await call_next(request)
                        logger.info("[STATUS CODE] Response: %s", response.status_code)
                        return response
                except Exception:
                    pass

            ip = request.headers.get("x-forwarded-for") or (
                request.client.host if request.client else ""
            )
            ip = ip.split(",")[0].strip()
            anonymous_uuid = request.cookies.get("anonymous_uuid")
            if not anonymous_uuid:
                logger.info("[STATUS CODE] Response: %s", 400)
                return JSONResponse(
                    status_code=400, content={"detail": "Anonymous UUID is required"}
                )
            anonymous_uuid = str(anonymous_uuid)
            rate_key = f"rate:{anonymous_uuid}_{ip}"
            count = await redis_client.incr(rate_key)
            if count == 1:
                await redis_client.expire(rate_key, RATE_WINDOW)
            if count > RATE_LIMIT:
                logger.warning(
                    "Rate limit exceeded for anonymous UUID: %s on IP: %s",
                    anonymous_uuid,
                    ip,
                )
                logger.info("[STATUS CODE] Response: %s", 429)
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests. Please try again later."},
                )
            if request.url.path.startswith("/api/recommendations"):
                response = await call_next(request)
                logger.info("[STATUS CODE] Response: %s", response.status_code)
                return response

            usage_key = f"usage:{anonymous_uuid}"
            usage = await redis_client.incr(usage_key)
            if usage == 1:
                await redis_client.expire(usage_key, MONTH_WINDOW)
            if usage > MONTH_LIMIT:
                logger.warning(
                    "Monthly limit exceeded for anonymous UUID: %s", anonymous_uuid
                )
                logger.info("[STATUS CODE] Response: %s", 429)
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Monthly limit exceeded. Please try again later."
                    },
                )
            response = await call_next(request)
            logger.info("[STATUS CODE] Response: %s", response.status_code)
            return response
        except RuntimeError as e:
            if "No response returned." in str(e) and await request.is_disconnected():
                logger.error("Request disconnected: %s", request.url)
                logger.info("[STATUS CODE] Response: %s", status.HTTP_204_NO_CONTENT)
                return Response(status_code=status.HTTP_204_NO_CONTENT)
            raise
        except Exception as e:
            logger.error("Error: %s", e)
            logger.info(
                "[STATUS CODE] Response: %s", status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            return JSONResponse(
                status_code=500, content={"detail": "Internal server error"}
            )
        finally:
            logger.info(
                "[END] Request processing time: %s seconds", time.time() - start
            )
