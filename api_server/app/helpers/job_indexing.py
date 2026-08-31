from app.db.arq import get_arq_pool
from app.services.job_service import store_jobs_to_pinecone

async def index_jobs_in_background(jobs: list) -> None:
    if not jobs:
        return
    try:
        pool = get_arq_pool()
        await pool.enqueue_job("store_jobs_to_pinecone_arq", jobs)
    except RuntimeError:
        # Worker process or tests: no API ARQ pool — index directly
        await store_jobs_to_pinecone(jobs)