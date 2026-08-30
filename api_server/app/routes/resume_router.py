import logging
from typing import Annotated

from fastapi import (APIRouter, Body, Depends, File, Header, HTTPException,
                     UploadFile, status, Cookie, Form, BackgroundTasks)
from fastapi.responses import JSONResponse

from app.auth.dependencies import get_current_user_id
from app.helpers.auth_helper import is_premium_user
from app.middlewares.limit import increment_monthly_usage
from app.ai_agents.free_tier_multiagents import build_free_tier_graph
from app.services.resume_analyzer import *
from app.services.resume_service import store_resume_to_mongodb

logger = logging.getLogger(__name__)

router = APIRouter(tags=["resumes"])


@router.post("/api/resume/analyze")
async def analyze_resume_free_tier(
    resume_pdf: Annotated[UploadFile, File(...)], # required
    jd_text: Annotated[str, Form()] = "", # optional
    user_goal: Annotated[str, Form()] = "", # optional
    anonymous_uuid: Annotated[str | None, Cookie()] = None
):
    try:
        resume_text = await extract_text_from_resume(resume_pdf)
        free_tier_analyzer = await build_free_tier_graph()
        state = {"resume_text": resume_text, "jd_text": jd_text, "user_goal": user_goal}
        result = await free_tier_analyzer.ainvoke(state)
        content = {
            "intent": result["intent"],
            "analyzer": result["analyzer"],
            "ats": result["ats"],
            "feedback": result["feedback"]
        }
        if anonymous_uuid:
            await increment_monthly_usage(anonymous_uuid)
        return JSONResponse(content=content, status_code=status.HTTP_200_OK)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing resume: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="INTERAL_SERVER_ERROR: An error occurred while analyzing the resume. Please try again later.")


@router.post("/api/resume/analyze/premium")
async def analyze_resume_premium(
    background_tasks: BackgroundTasks,
    resume_pdf: Annotated[UploadFile, File(...)], # required
    jd_text: Annotated[str, Form()] = "", # optional
    user_goal: Annotated[str, Form()] = "", # optional
    includes_job_finder: Annotated[bool, Form()] = False, # optional
    is_premium_user: Annotated[bool, Depends(is_premium_user)] = False,
    current_user_id: Annotated[int, Depends(get_current_user_id)] = None,
):
    """
    Analyze the resume for premium users
    Description:
    - Work the same as the free tier analyzer, but with more advanced features
    - Store the resume to MongoDB in the background
    System parameters:
    - background_tasks: The background tasks from FastAPI to store resume to MongoDB, S3
    - current_user_id: The ID of the current user, to track the usage
    - is_premium_user: Whether the current user is a premium user
    Must have parameters from client:
    - resume_pdf: The resume PDF file
    - jd_text: The job description text
    - user_goal: The user's goal
    - includes_job_finder: Whether to include the job finder
    Returns:
    - The analysis result in JSON format
    """
    if not is_premium_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action is only available to PREMIUM users."
        )
