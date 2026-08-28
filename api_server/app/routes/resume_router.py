import logging
from typing import Annotated

from fastapi import (APIRouter, Body, Depends, File, Header, HTTPException,
                     UploadFile, status, Cookie, Form, BackgroundTasks)
from fastapi.responses import JSONResponse

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
    anonymous_uuid: Annotated[str | None, Cookie()] = None
):
    """
    Analyze the resume for premium users
    Description:
    - Work the same as the free tier analyzer, but with more advanced features
    - Store the resume to MongoDB in the background
    Parameters:
    - resume_pdf: The resume PDF file
    - jd_text: The job description text
    - user_goal: The user's goal
    - anonymous_uuid: The anonymous UUID of the user
    - background_tasks: The background tasks
    Returns:
    - The analysis result in JSON format
    """
    pass
