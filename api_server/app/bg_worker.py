import logging
from arq.connections import RedisSettings

from app.core.config import settings
from app.db.mongo import init_mongo, close_mongo
from app.db.pinecone import init_pinecone, close_pinecone
from app.db.s3 import init_s3_client, close_s3_client
from app.services.job_service import store_jobs_to_pinecone
from app.services.resume_service import store_resume_to_mongodb
import asyncio

logger = logging.getLogger(__name__)

async def startup(ctx):
    await asyncio.gather(
        init_mongo(),
        init_pinecone(),
        init_s3_client()
    )
    logger.info("Background ARQ worker started")

async def shutdown(ctx):
    await asyncio.gather(
        close_mongo(),
        close_pinecone(),
        close_s3_client()
    )
    logger.info("Background ARQ worker stopped")

async def store_jobs_to_pinecone_arq(ctx, jobs: list):
    await store_jobs_to_pinecone(jobs)
    logger.info(f"Jobs stored to Pinecone: {len(jobs)}")

async def store_resume_to_mongodb_arq(ctx, user_id: int, resume_filename: str, pdf_bytes: bytes, analyzed_result: dict):
    await store_resume_to_mongodb(user_id, resume_filename, pdf_bytes, analyzed_result)
    logger.info(f"Resume stored to MongoDB: {resume_filename}")

class WorkerSettings:
    functions = [
        store_jobs_to_pinecone_arq,
        store_resume_to_mongodb_arq
    ]
    redis_settings = RedisSettings(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        database=settings.REDIS_ARQ_DB,
    )
    on_startup = startup
    on_shutdown = shutdown
    max_jobs = 5
    job_timeout = 1000
    max_tries = 3