from fastapi import APIRouter, Depends, HTTPException, Header, status, File, Body, UploadFile
from fastapi.responses import JSONResponse
from app.services.resume_analyzer import *
from app.ai_agents.agent1_intent import intent_goal_agent
from app.ai_agents.agent6_finalizer import resume_feedback_free_tier
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["resumes"])


@router.post("/api/resume/analyze")
async def analyze_resume_free_tier(resume_pdf: UploadFile = File(...), jd_text: str = Body(default=""), user_goal: str = Body(default="")):
    try:
        resume_text = await extract_text_from_resume(resume_pdf)
        has_jd = bool(jd_text and jd_text.strip())
        has_goal = bool(user_goal and user_goal.strip())

        if not has_jd and not has_goal:
            agent1_response = await intent_goal_agent(resume_text)

            # Get industry from agent1_response
            industry = agent1_response["industry"]

            # extract_skills_from_text_without_jd
            skills = extract_skills_from_text_without_jd(resume_text, industry)

            # calculate_resume_quality_score_for_free_tier
            resume_quality_score, necessary_sections_score, metrics_score = calculate_resume_quality_score_for_free_tier(
                resume_text, False)

            # give the response to agent6_finalizer
            agent6_response = await resume_feedback_free_tier(resume_text, skills["skills"] + skills["soft_skills"], None, None, resume_quality_score, 0, metrics_score, necessary_sections_score)

            content = {
                "feedback": agent6_response,
                "industry": industry,
                "soft_skills": skills["soft_skills"],
                "hard_skills": skills["skills"],
                "resume_quality_score": resume_quality_score,
                "necessary_sections_score": necessary_sections_score,
                "metrics_score": metrics_score
            }
            return JSONResponse(content=content, status_code=status.HTTP_200_OK)

        elif has_jd and has_goal:
            agent1_response = await intent_goal_agent(resume_text, jd_text, user_goal)

            industry = agent1_response["industry"]

            # extract_skills_from_text_without_jd
            skills = extract_skills_from_text_with_jd(resume_text, jd_text)

            # calculate_resume_quality_score_for_free_tier
            resume_quality_score, necessary_sections_score, metrics_score = calculate_resume_quality_score_for_free_tier(
                resume_text, True, jd_text)

            # give the response to agent6_finalizer
            agent6_response = await resume_feedback_free_tier(resume_text, skills["skills"] + skills["soft_skills"], jd_text, skills["missing_skills"], resume_quality_score, skills["matching_skills_score"], metrics_score, necessary_sections_score, user_goal)

            content = {
                "feedback": agent6_response,
                "industry": industry,
                "soft_skills": skills["soft_skills"],
                "hard_skills": skills["skills"],
                "resume_quality_score": resume_quality_score,
                "necessary_sections_score": necessary_sections_score,
                "metrics_score": metrics_score
            }
            return JSONResponse(content=content, status_code=status.HTTP_200_OK)

        elif has_jd:

            agent1_response = await intent_goal_agent(resume_text, jd_text)

            industry = agent1_response["industry"]

            # extract_skills_from_text_without_jd
            skills = extract_skills_from_text_with_jd(resume_text, jd_text)

            # calculate_resume_quality_score_for_free_tier
            resume_quality_score, necessary_sections_score, metrics_score = calculate_resume_quality_score_for_free_tier(
                resume_text, True, jd_text)

            # give the response to agent6_finalizer
            agent6_response = await resume_feedback_free_tier(resume_text, skills["skills"] + skills["soft_skills"], jd_text, skills["missing_skills"], resume_quality_score, skills["matching_skills_score"], metrics_score, necessary_sections_score)

            content = {
                "feedback": agent6_response,
                "industry": industry,
                "soft_skills": skills["soft_skills"],
                "hard_skills": skills["skills"],
                "resume_quality_score": resume_quality_score,
                "necessary_sections_score": necessary_sections_score,
                "metrics_score": metrics_score
            }
            return JSONResponse(content=content, status_code=status.HTTP_200_OK)

        elif has_goal:
            agent1_response = await intent_goal_agent(resume_text, user_goal=user_goal)

            # Get industry from agent1_response
            industry = agent1_response["industry"]

            # extract_skills_from_text_without_jd
            skills = extract_skills_from_text_without_jd(resume_text, industry)

            # calculate_resume_quality_score_for_free_tier
            resume_quality_score, necessary_sections_score, metrics_score = calculate_resume_quality_score_for_free_tier(
                resume_text, False)

            # give the response to agent6_finalizer
            agent6_response = await resume_feedback_free_tier(resume_text, skills["skills"] + skills["soft_skills"], None, None, resume_quality_score, 0, metrics_score, necessary_sections_score, user_goal)

            content = {
                "feedback": agent6_response,
                "industry": industry,
                "soft_skills": skills["soft_skills"],
                "hard_skills": skills["skills"],
                "resume_quality_score": resume_quality_score,
                "necessary_sections_score": necessary_sections_score,
                "metrics_score": metrics_score
            }
            return JSONResponse(content=content, status_code=status.HTTP_200_OK)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing resume: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal server error while analyzing resume")