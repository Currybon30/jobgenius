from typing import Annotated
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from app.ai_agents.agents.agent7_jobfinder import jobfinder_agent
from app.services.resume_analyzer import extract_text_from_resume
from app.auth.dependencies import get_current_user_id
import logging
from app.db.redis import get_redis_client
from app.helpers.auth_helper import is_premium_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/api/job/search/with/prompt")
async def search_jobs_with_prompt(
    resume_pdf: Annotated[UploadFile, File(...)],
    prompt: Annotated[str, Form(...)],
    current_user_id: Annotated[int, Depends(get_current_user_id)] = None,
    is_premium_user: Annotated[bool, Depends(is_premium_user)] = False,
):
    """
    Search jobs with a prompt. Users must login to use this endpoint.
    Free users are limited to get the jobs by their own resume and prompt once every 10 days.
    Premium users are limited to the number of times they can use this endpoint once every day.
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
        if not current_user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
        redis_client = get_redis_client()
        if not is_premium_user:
            limit_cache_key = f"job_search_with_prompt_free_limit:{current_user_id}"
            limit = await redis_client.get(limit_cache_key)
            if limit:
                return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": "You have reached the limit of job search with prompt. Please try again later."})
            else:
                await redis_client.set(limit_cache_key, 1, ex=60 * 60 * 24 * 10) # 10 days
        else:
            limit_cache_key = f"job_search_with_prompt_premium_limit:{current_user_id}"
            limit = await redis_client.get(limit_cache_key)
            if limit:
                return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": "You have reached the limit of job search with prompt. Please try again later."})
            else:
                await redis_client.set(limit_cache_key, 1, ex=60 * 60 * 24) # 1 day

        resume_text = await extract_text_from_resume(resume_pdf)
        if not resume_text:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to extract text from resume")
        result = await jobfinder_agent(resume_text=resume_text, user_requirements=prompt)
        # Format the result to be more readable
        return JSONResponse(status_code=status.HTTP_200_OK, content={"jobs": result}) #!TODO: Format the result to be more readable
    except Exception as e:
        logger.error(f"Error searching jobs with prompt: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")