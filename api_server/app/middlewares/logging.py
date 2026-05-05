import logging

from fastapi import Request

logger = logging.getLogger(__name__)


async def logging_middleware(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")

    response = await call_next(request)

    logger.info(f"Status: {response.status_code}")
    return response
