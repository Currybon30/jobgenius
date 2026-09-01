import hashlib
import json
import logging
from typing import Annotated

from app.db.arq import get_arq_pool
from app.db.redis import get_redis_client
from app.helpers.auth_helper import is_premium_user
from app.helpers.user_helper import get_user_city_and_country
from app.services.job_service import search_jobs
from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.get("/recommendations")
async def get_job_recommendations_unlogged_in_user(
    request: Request, industry: Annotated[str, Query("any job")]
):
    try:
        arq_pool = get_arq_pool()
        redis_client = get_redis_client()
        anonymous_uuid = request.cookies.get("anonymous_uuid")
        if not anonymous_uuid:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Anonymous UUID not found"},
            )
        anonymous_uuid = str(anonymous_uuid)
        ip = request.headers.get("x-forwarded-for") or (request.client.host if request.client else None)
        ip_address = ip.split(",")[0].strip() if ip else None
        city, country, country_code = await get_user_city_and_country(ip_address)
        if not city or not country or not country_code:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Failed to get user's city and country"},
            )

        cache_input = f"{anonymous_uuid}_{industry.lower().strip()}_{city}_{country}_{country_code}".lower().strip()
        cache_hash = hashlib.sha256(cache_input.encode()).hexdigest()[:16]
        recommendations_cache_key = f"recommendations_cache:{cache_hash}"
        recommendations = await redis_client.get(recommendations_cache_key)
        if recommendations:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"jobs": json.loads(recommendations)},
            )

        query = f"{industry} in {city}, {country}"
        jobs = await search_jobs(query, country=country_code, language="en")
        if not jobs:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"error": "No jobs found"},
            )
        bg_job = await arq_pool.enqueue_job("store_jobs_to_pinecone_arq", jobs)
        if bg_job:
            storage_status = "enqueued"
        else:
            storage_status = "error"
        await redis_client.set(
            recommendations_cache_key, json.dumps(jobs), ex=60 * 60 * 24 * 15 # 15 days
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"jobs": jobs, "storage_status": storage_status},
        )
    except Exception as e:
        logger.error(f"Error getting job recommendations: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Failed to get job recommendations"},
        )


@router.get("/recommendations/free")
async def get_job_recommendations_free_user(request: Request):
    pass


@router.get("/recommendations/premium")
async def get_job_recommendations_premium_user(
    request: Request, is_premium_user: Annotated[bool, Depends(is_premium_user)] = False
):
    pass
