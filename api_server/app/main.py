import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.db.base import Base
from app.db.s3 import init_s3_client, close_s3_client
from app.db.redis import close_redis, init_redis
from app.db.mongo import close_mongo, init_mongo
from app.db.pinecone import close_pinecone, init_pinecone
from app.core.ollama_config import close_ollama, init_ollama
from app.db.session import engine
from app.middlewares.limit import rate_limit_middleware
from app.middlewares.logging import logging_middleware
from app.middlewares.timing import timing_middleware
from app.routes.resume_router import router as resume_router
from app.routes.user_router import router as user_router
from app.routes.job_recommender_router import router as job_recommender_router
import asyncio

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # STARTUP LOGIC
        logger.info("Initializing application...")
        await asyncio.gather(init_redis(), init_mongo(), init_pinecone(), init_ollama(), init_s3_client())
        Base.metadata.create_all(bind=engine)

        yield
    except Exception:
        logger.error("Error during application lifespan")
        raise
    finally:
        # SHUTDOWN LOGIC
        logger.info("Shutting down application...")
        await asyncio.gather(close_redis(), close_mongo(), close_pinecone(), close_ollama(), close_s3_client())

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

app.middleware("http")(logging_middleware)
app.middleware("http")(rate_limit_middleware)
app.middleware("http")(timing_middleware)

app.include_router(user_router)
app.include_router(resume_router)
app.include_router(job_recommender_router)