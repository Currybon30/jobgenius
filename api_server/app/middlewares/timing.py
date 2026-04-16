import time
import logging
from fastapi import Request

logger = logging.getLogger(__name__)

async def timing_middleware(request: Request, call_next):
    start = time.time()

    response = await call_next(request)

    duration = time.time() - start
    response.headers["X-Process-Time"] = str(duration)
    logger.info(f"Processed {request.method} {request.url} in {duration:.4f} seconds")

    return response