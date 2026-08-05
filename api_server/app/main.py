import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.db.base import Base
from app.db.redis import close_redis, init_redis
from app.db.session import engine
from app.middlewares.limit import rate_limit_middleware
from app.middlewares.logging import logging_middleware
from app.middlewares.timing import timing_middleware
from app.routes.resume_router import router as resume_router
from app.routes.user_router import router as user_router

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # STARTUP LOGIC
        logger.info("Initializing application...")
        await init_redis()
        Base.metadata.create_all(bind=engine)

        yield

        # SHUTDOWN LOGIC
        logger.info("Shutting down application...")
        await close_redis()
    except Exception:
        logger.error("Error during application lifespan")
        raise

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

app.include_router(user_router)
app.include_router(resume_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}

app.middleware("http")(logging_middleware)
app.middleware("http")(rate_limit_middleware)
app.middleware("http")(timing_middleware)
