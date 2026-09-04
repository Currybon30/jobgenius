import logging
from typing import Annotated

from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import JSONResponse

from app.ai_agents.free_tier_multiagents import GraphState as FreeTierGraphState
from app.ai_agents.free_tier_multiagents import build_free_tier_graph
from app.ai_agents.premium_multiagents import GraphState as PremiumGraphState
from app.ai_agents.premium_multiagents import build_premium_graph
from app.auth.dependencies import get_current_user_id
from app.db.arq import get_arq_pool
from app.db.redis import get_redis_client
from app.helpers.auth_helper import is_premium_user
from app.helpers.limit_helper import increment_monthly_usage
from app.services.resume_analyzer import convert_file_to_bytes, extract_text_from_resume
from app.services.resume_service import (
    delete_resume_by_id_and_version,
    get_resume_by_id_and_version_from_mongodb,
    get_resume_by_id_from_mongodb,
    get_resumes_from_mongodb,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["resumes"])


@router.post("/api/resume/analyze")
async def analyze_resume_free_tier(
    resume_pdf: Annotated[UploadFile, File(...)],  # required
    jd_text: Annotated[str, Form()] = "",  # optional
    user_goal: Annotated[str, Form()] = "",  # optional
    anonymous_uuid: Annotated[str | None, Cookie()] = None,
):
    try:
        resume_bytes = await convert_file_to_bytes(resume_pdf)
        resume_text = extract_text_from_resume(resume_pdf, resume_bytes)
        free_tier_analyzer = await build_free_tier_graph()
        state: FreeTierGraphState = {
            "resume_text": resume_text,
            "jd_text": jd_text,
            "user_goal": user_goal,
            "intent": {},
            "analyzer": {},
            "ats": {},
            "feedback": {},
        }
        result = await free_tier_analyzer.ainvoke(state)
        content = {
            "intent": result["intent"],
            "analyzer": result["analyzer"],
            "ats": result["ats"],
            "feedback": result["feedback"],
        }
        if anonymous_uuid:
            await increment_monthly_usage(anonymous_uuid)
        return JSONResponse(content=content, status_code=status.HTTP_200_OK)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="INTERNAL_SERVER_ERROR: An error occurred while analyzing the resume. Please try again later.",
        )


@router.post("/api/resume/analyze/premium")
async def analyze_resume_premium(
    resume_pdf: Annotated[UploadFile, File(...)],  # required
    jd_text: Annotated[str, Form()] = "",  # optional
    user_goal: Annotated[str, Form()] = "",  # optional
    includes_job_finder: Annotated[bool, Form()] = False,  # optional
    is_premium_user: Annotated[bool, Depends(is_premium_user)] = False,
    current_user_id: Annotated[int, Depends(get_current_user_id)] = -1,
):
    """
    Analyze the resume for premium users
    Description:
    - Work the same as the free tier analyzer, but with more advanced features
    - Store the resume to MongoDB in the background
    System parameters:
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
            detail="This action is only available to PREMIUM users.",
        )
    try:
        redis_client = get_redis_client()
        usage_key = f"premium_resume_analyzer_usage:{current_user_id}"
        usage = await redis_client.get(usage_key)
        if not usage:
            await redis_client.set(usage_key, 0)
        elif int(usage) >= 3:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You have reached the maximum number of resume analyses for today. Please try again tomorrow.",
            )
        arq_pool = get_arq_pool()
        message = ""
        job_finder_usage_key = ""
        if includes_job_finder:
            job_finder_usage_key = (
                f"job_search_with_prompt_premium_limit:{current_user_id}"
            )
            job_finder_usage = await redis_client.get(job_finder_usage_key)
            if not job_finder_usage or int(job_finder_usage) < 1:
                await redis_client.set(job_finder_usage_key, 0)
            elif job_finder_usage and int(job_finder_usage) >= 1:
                message = "You have reached the maximum number of job finder calls for 3 days. We will disable the job finder feature for you in this session. Please try again in 3 days."
                includes_job_finder = False

        resume_bytes = await convert_file_to_bytes(resume_pdf)
        resume_text = extract_text_from_resume(resume_pdf, resume_bytes)
        premium_analyzer = await build_premium_graph()
        state: PremiumGraphState = {
            "resume_text": resume_text,
            "jd_text": jd_text,
            "user_goal": user_goal,
            "includes_job_finder": includes_job_finder,
            "intent": {},
            "analyzer": {},
            "ats": {},
            "optimizer": {},
            "feedback": {},
            "job_finder": {},
        }
        result = await premium_analyzer.ainvoke(state)
        content = {
            "intent": result["intent"],
            "analyzer": result["analyzer"],
            "ats": result["ats"],
            "optimizer": result["optimizer"],
            "feedback": result["feedback"],
            "job_finder": result.get("job_finder") if includes_job_finder else None,
        }
        if message:
            content["message"] = message

        await arq_pool.enqueue_job(
            "store_resume_to_mongodb_arq",
            current_user_id,
            resume_pdf.filename,
            resume_bytes,
            result,
        )
        await redis_client.incr(usage_key)
        await redis_client.expire(usage_key, 60 * 60 * 24)
        job_finder = content.get("job_finder") or {}
        job_finder_jobs = job_finder.get("jobs") or []
        if includes_job_finder and job_finder and len(job_finder_jobs) > 0:
            await redis_client.incr(job_finder_usage_key)
            await redis_client.expire(job_finder_usage_key, 60 * 60 * 24 * 3)
        return JSONResponse(content=content, status_code=status.HTTP_200_OK)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="INTERNAL_SERVER_ERROR: An error occurred while analyzing the resume. Please try again later.",
        )


@router.get("/api/resumes")
async def get_resumes(
    current_user_id: Annotated[int, Depends(get_current_user_id)],
):
    try:
        resumes = await get_resumes_from_mongodb(current_user_id)
        return JSONResponse(content=resumes, status_code=status.HTTP_200_OK)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting resumes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="INTERNAL_SERVER_ERROR: An error occurred while getting the resumes. Please try again later.",
        )


@router.get("/api/resumes/{resume_id}")
async def get_resume(
    resume_id: str,
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    version: Annotated[int | None, Query()] = None,
):
    try:
        if version is None:
            resume = await get_resume_by_id_from_mongodb(current_user_id, resume_id)
            return JSONResponse(content=resume, status_code=status.HTTP_200_OK)
        else:
            resume = await get_resume_by_id_and_version_from_mongodb(
                current_user_id, resume_id, version
            )
            return JSONResponse(content=resume, status_code=status.HTTP_200_OK)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="INTERNAL_SERVER_ERROR: An error occurred while getting the resume. Please try again later.",
        )


@router.delete("/api/resumes/{resume_id}")
async def delete_resume(
    resume_id: str,
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    version: Annotated[int, Query()],
):
    try:
        await delete_resume_by_id_and_version(
            current_user_id, resume_id, version
        )
        return JSONResponse(
            content={"message": "Resume deleted successfully."},
            status_code=status.HTTP_200_OK,
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="INTERNAL_SERVER_ERROR: An error occurred while deleting the resume. Please try again later.",
        )
