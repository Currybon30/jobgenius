import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from app.ai_agents.agents.agent7_jobfinder import jobfinder_agent
from app.auth.dependencies import get_current_user_id
from app.db.redis import get_redis_client
from app.helpers.auth_helper import is_premium_user
from app.helpers.job_indexing import schedule_job_indexing
from app.helpers.llm_call import agent7_jobfinder_format_result
from app.services.resume_analyzer import convert_file_to_bytes, extract_text_from_resume

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/api/job/search/with/prompt")
async def search_jobs_with_prompt(
    resume_pdf: Annotated[UploadFile, File(...)],
    prompt: Annotated[str, Form(...)],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    is_premium_user: Annotated[bool, Depends(is_premium_user)] = False,
):
    """
    Search jobs with a prompt. Users must login to use this endpoint.
    Free users are limited to get the jobs by their own resume and prompt once every 15 days.
    Premium users are limited to the number of times they can use this endpoint once 3 days.
    System parameters:
    - current_user_id: The ID of the current user, to track the usage
    - is_premium_user: Whether the current user is a premium user
    Must have parameters from client:
    - resume_pdf: The resume PDF file
    - prompt: The prompt
    Returns:
    - The jobs in JSON format
    """
    try:
        redis_client = get_redis_client()
        limit_cache_key = (
            f"job_search_with_prompt_premium_limit:{current_user_id}"
            if is_premium_user
            else f"job_search_with_prompt_free_limit:{current_user_id}"
        )
        if not is_premium_user:
            limit = await redis_client.get(limit_cache_key)
            if limit and int(limit) >= 1:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You have reached the limit of job search with prompt. Please try again later.",
                )
            elif not limit or int(limit) < 1:
                await redis_client.set(limit_cache_key, 0)
        else:
            limit = await redis_client.get(limit_cache_key)
            if limit and int(limit) >= 1:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You have reached the limit of job search with prompt. Please try again later.",
                )
            elif not limit or int(limit) < 1:
                await redis_client.set(limit_cache_key, 0)

        resume_bytes = await convert_file_to_bytes(resume_pdf)
        resume_text = extract_text_from_resume(resume_pdf, resume_bytes)
        if not resume_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to extract text from resume",
            )
        messages, raw_jobs = await jobfinder_agent(
            resume_text=resume_text, user_requirements=prompt
        )
        jobfinder_result = agent7_jobfinder_format_result(messages, raw_jobs)
        if jobfinder_result.get("error") and not jobfinder_result.get("jobs"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=jobfinder_result["error"],
            )
        message = jobfinder_result["message"]
        jobs = jobfinder_result.get("jobs") or []
        if jobs:
            schedule_job_indexing(jobs)
            await redis_client.incr(limit_cache_key)
            if not is_premium_user:
                await redis_client.expire(limit_cache_key, 60 * 60 * 24 * 15)
            else:
                await redis_client.expire(limit_cache_key, 60 * 60 * 24 * 3)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": message, "jobs": jobs},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching jobs with prompt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
