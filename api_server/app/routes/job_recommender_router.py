import hashlib
import json
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse

from app.ai_agents.agents.agent7_jobfinder import jobfinder_agent
from app.auth.dependencies import get_current_user_id
from app.db.arq import get_arq_pool
from app.db.redis import get_redis_client
from app.helpers.auth_helper import is_premium_user
from app.helpers.llm_call import agent7_jobfinder_format_result
from app.helpers.user_helper import get_user_city_and_country
from app.schemas.user import UserResponse
from app.services.job_service import job_recommendation_with_pinecone, search_jobs
from app.services.resume_service import (
    get_resume_for_job_recommendation_from_mongodb,
    resolve_resume_id_for_recommendations,
)
from app.services.user_service import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

UNLOGGED_IN_RECOMMENDATIONS_CACHE_TTL = 60 * 60 * 24 * 15  # 15 days
FREE_RECOMMENDATIONS_CACHE_TTL = 60 * 60 * 24 * 10  # 10 days
PREMIUM_RECOMMENDATIONS_CACHE_TTL = 60 * 60 * 24 * 3  # 3 days


async def _cache_and_return_premium_recommendations(
    redis_client,
    cache_key: str,
    content: dict,
) -> JSONResponse:
    await redis_client.set(
        cache_key,
        json.dumps(content),
        ex=PREMIUM_RECOMMENDATIONS_CACHE_TTL,
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content=content)


@router.get("/recommendations")
async def get_job_recommendations_unlogged_in_user(request: Request):
    try:
        arq_pool = get_arq_pool()
        redis_client = get_redis_client()
        anonymous_uuid = request.cookies.get("anonymous_uuid")
        if not anonymous_uuid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Anonymous UUID not found",
            )
        anonymous_uuid = str(anonymous_uuid)
        ip = request.headers.get("x-forwarded-for") or (
            request.client.host if request.client else None
        )
        ip_address = ip.split(",")[0].strip() if ip else None
        city, country, country_code = await get_user_city_and_country(ip_address)
        if not city or not country or not country_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user's city and country",
            )

        cache_input = f"{anonymous_uuid}_{city}_{country_code}".lower().strip()
        cache_hash = hashlib.sha256(cache_input.encode()).hexdigest()[:16]
        recommendations_cache_key = f"recommendations_cache:{cache_hash}"
        recommendations = await redis_client.get(recommendations_cache_key)
        if recommendations:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "provider": "search_jobs",
                    "jobs": json.loads(recommendations),
                },
            )

        query = f"any job in {city}, {country}"
        jobs = await search_jobs(query, country=country_code, language="en")
        if not jobs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No jobs found"
            )
        await arq_pool.enqueue_job("store_jobs_to_pinecone_arq", jobs)
        await redis_client.set(
            recommendations_cache_key,
            json.dumps(jobs),
            ex=UNLOGGED_IN_RECOMMENDATIONS_CACHE_TTL,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"provider": "search_jobs", "jobs": jobs},
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"No jobs found: {e!s}"
        )
    except Exception as e:
        logger.error(f"Error getting job recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get job recommendations",
        )


@router.get("/recommendations/free")
async def get_job_recommendations_free_user(
    request: Request,
    industry: Annotated[str, Query("any job")],
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """
    Get job recommendations for a free user.
    Description:
    - If the user has not run the analysis, the industry parameter is any job by default.
    - If the user has run the analysis, the industry parameter is the industry of the resume.
    - Returned jobs from job search API will be stored in Redis cache for 10 days.
    Args:
        request: Request object
        industry: Industry to search for
        current_user: Current user object
    Returns:
        JSONResponse: JSON response containing job recommendations
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    try:
        arq_pool = get_arq_pool()
        redis_client = get_redis_client()
        ip = request.headers.get("x-forwarded-for") or (
            request.client.host if request.client else None
        )
        ip_address = ip.split(",")[0].strip() if ip else None
        city, country, country_code = await get_user_city_and_country(ip_address)
        if not city or not country or not country_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user's city and country",
            )

        normalized_industry = industry.lower().strip()
        cache_input = f"{current_user.uid}_{normalized_industry}_{city}_{country_code}".lower().strip()
        cache_hash = hashlib.sha256(cache_input.encode()).hexdigest()[:16]
        recommendations_cache_key = f"recommendations_cache:free:{cache_hash}"
        recommendations = await redis_client.get(recommendations_cache_key)
        if recommendations:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "provider": "search_jobs",
                    "jobs": json.loads(recommendations),
                },
            )

        query = f"{industry.strip()} in {city}, {country}"
        jobs = await search_jobs(query, country=country_code, language="en")
        if not jobs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No jobs found"
            )
        await arq_pool.enqueue_job("store_jobs_to_pinecone_arq", jobs)
        await redis_client.set(
            recommendations_cache_key,
            json.dumps(jobs),
            ex=FREE_RECOMMENDATIONS_CACHE_TTL,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"provider": "search_jobs", "jobs": jobs},
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"No jobs found: {e!s}"
        )
    except Exception as e:
        logger.error(f"Error getting free job recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get job recommendations",
        )


@router.get("/recommendations/premium")
async def get_job_recommendations_premium_user(
    request: Request,
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    is_premium: Annotated[bool, Depends(is_premium_user)],
    resume_id: Annotated[str | None, Query()] = None,
):
    """
    Get job recommendations for a premium user.
    Uses Pinecone similarity on stored resume text; falls back to jobfinder agent
    when no Pinecone matches are found.
    """
    if not is_premium:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action is only available to PREMIUM users.",
        )
    try:
        resolved_resume_id = await resolve_resume_id_for_recommendations(
            current_user_id, resume_id
        )
        redis_client = get_redis_client()
        arq_pool = get_arq_pool()
        ip = request.headers.get("x-forwarded-for") or (
            request.client.host if request.client else None
        )
        ip_address = ip.split(",")[0].strip() if ip else None
        city, country, country_code = await get_user_city_and_country(ip_address)

        cache_input = f"{current_user_id}_{resolved_resume_id}_{city}_{country_code}".lower().strip()
        cache_hash = hashlib.sha256(cache_input.encode()).hexdigest()[:16]
        recommendations_cache_key = f"recommendations_cache:premium:{cache_hash}"
        cached = await redis_client.get(recommendations_cache_key)
        if cached:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=json.loads(cached),
            )

        result = await job_recommendation_with_pinecone(
            resolved_resume_id,
            job_city=city or "",
            job_country=country_code or "",
        )

        if isinstance(result, list) and result:
            return await _cache_and_return_premium_recommendations(
                redis_client,
                recommendations_cache_key,
                {"provider": "pinecone", "jobs": result},
            )

        if isinstance(result, dict) and result.get("error"):
            resume_text = result.get("resume_text") or ""
            if not resume_text:
                stored = await get_resume_for_job_recommendation_from_mongodb(
                    resolved_resume_id
                )
                resume_text = (stored or {}).get("full_combined_text") or ""

            if not resume_text:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=result["error"]
                )
            if not city or not country:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user's city and country",
                )

            user_requirements = (
                f"I have provided my resume text. Help me find the best jobs for me "
                f"in {city}, {country}."
            )
            agent_messages, raw_jobs = await jobfinder_agent(
                resume_text=resume_text,
                user_requirements=user_requirements,
            )
            formatted_response = agent7_jobfinder_format_result(
                agent_messages, raw_jobs
            )
            if formatted_response.get("error"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=formatted_response["error"],
                )

            jobs = formatted_response.get("jobs") or []
            if not jobs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="No jobs found"
                )
            await arq_pool.enqueue_job("store_jobs_to_pinecone_arq", jobs)
            return await _cache_and_return_premium_recommendations(
                redis_client,
                recommendations_cache_key,
                {"provider": "agent7_jobfinder", "jobs": jobs},
            )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No jobs found"
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"No jobs found: {e!s}"
        )
    except Exception as e:
        logger.error(f"Error getting premium job recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get job recommendations",
        )
