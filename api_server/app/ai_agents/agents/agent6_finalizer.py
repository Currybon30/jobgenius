import json
import logging
from typing import Any, Optional

from app.helpers.llm_call import llm_call, safe_parse

logger = logging.getLogger(__name__)


def _pct(value: Any) -> float:
    """Normalize a 0–1 or already-percentage score to 0–100."""
    try:
        score = float(value)
    except (TypeError, ValueError):
        return 0.0
    if score <= 1.0:
        return round(score * 100, 2)
    return round(score, 2)


def _json_block(data: Any) -> str:
    return json.dumps(data, indent=2, default=str, ensure_ascii=False)


async def finalizer_agent_free_tier(
    resume_text: str,
    intent: dict,
    analyzer: dict,
    ats: dict,
    user_goal: Optional[str] = None,
):
    """
    Agent 6 — final free-tier feedback.

    Args:
        resume_text: Original resume text.
        intent: Agent 1 output (target role, goals, keywords, strategy).
        analyzer: Agent 2 output (sections, skills, JD match fields if any).
        ats: Agent 3 output (resume quality / ATS scores).
        user_goal: Optional original user goal string.
    """
    intent = intent or {}
    analyzer = analyzer or {}
    ats = ats or {}

    jd_provided = bool(analyzer.get("jd_provided"))
    jd_text = analyzer.get("jd_text") or ""
    if not user_goal:
        user_goal = "No specific goal provided."

    # Agent 1 fields used for light personalization (still free-tier / general)
    target_role = intent.get("target_role", "")
    seniority_level = intent.get("seniority_level", "")
    industry = intent.get("industry", "")
    priority_goals = intent.get("priority_goals", [])
    focus_areas = intent.get("focus_areas", [])
    top_keywords = intent.get("top_keywords", [])
    optimization_strategy = intent.get("optimization_strategy", {})

    # Agent 2 — structure & skills
    hard_skills = analyzer.get("hard_skills", [])
    soft_skills = analyzer.get("soft_skills", [])
    years_exp = analyzer.get("years_exp", 0)
    section_flags = {
        "has_summary": analyzer.get("has_summary", False),
        "has_skills": analyzer.get("has_skills", False),
        "has_experience": analyzer.get("has_experience", False),
        "has_projects": analyzer.get("has_projects", False),
        "has_education": analyzer.get("has_education", False),
        "has_metrics": analyzer.get("has_metrics", False),
        "has_contact": bool(analyzer.get("emails") or analyzer.get("phone_numbers")),
    }

    missing_hard_skills = analyzer.get("missing_hard_skills", [])
    missing_soft_skills = analyzer.get("missing_soft_skills", [])
    matching_hard_skills_score = _pct(analyzer.get("matching_hard_skills_score", 0))
    matching_soft_skills_score = _pct(analyzer.get("matching_soft_skills_score", 0))

    # Agent 3 — quality / ATS scores
    resume_score = _pct(ats.get("resume_score", 0))
    section_score = _pct(ats.get("section_score", 0))
    experience_projects_score = _pct(ats.get("experience_projects_score", 0))
    skills_quality_score = _pct(ats.get("skills_quality_score", 0))
    summary_quality_score = _pct(ats.get("summary_quality_score", 0))
    formatting_score = _pct(ats.get("formatting_score", 0))
    ats_score = ats.get("ats_score")  # already 0–100 when present
    hard_match_ats = ats.get("hard_skills_score")
    soft_match_ats = ats.get("soft_skills_score")

    if jd_provided:
        jd_scores_block = f"""
            === AGENT 2 — JD SKILL MATCH ===
            Hard skills on resume: {_json_block(hard_skills)}
            Soft skills on resume: {_json_block(soft_skills)}
            Missing hard skills (in JD, not on resume): {_json_block(missing_hard_skills)}
            Missing soft skills (in JD, not on resume): {_json_block(missing_soft_skills)}
            Matching hard skills score: {matching_hard_skills_score}%
            Matching soft skills score: {matching_soft_skills_score}%

            Job description (reference only; do not quote at length):
            {jd_text[:2000]}

            === AGENT 3 — QUALITY & ATS SCORES ===
            - Overall Resume Score: {resume_score}%
            - Necessary Sections Score: {section_score}%
            - Experience/Projects Score: {experience_projects_score}%
            - Skills Quality Score: {skills_quality_score}%
            - Summary Quality Score: {summary_quality_score}%
            - Formatting Score: {formatting_score}%
            - ATS Fit Score: {ats_score if ats_score is not None else "N/A"}%
            - Hard Skills Match (ATS): {hard_match_ats if hard_match_ats is not None else "N/A"}%
            - Soft Skills Match (ATS): {soft_match_ats if soft_match_ats is not None else "N/A"}%
            """
    else:
        jd_scores_block = f"""
            === AGENT 2 — DETECTED SKILLS (no JD) ===
            Hard skills: {_json_block(hard_skills)}
            Soft skills: {_json_block(soft_skills)}
            No job description was provided — do NOT invent missing skills, JD fit, or matching scores.

            === AGENT 3 — QUALITY SCORES (no JD) ===
            - Overall Resume Score: {resume_score}%
            - Necessary Sections Score: {section_score}%
            - Experience/Projects Score: {experience_projects_score}%
            - Skills Quality Score: {skills_quality_score}%
            - Summary Quality Score: {summary_quality_score}%
            - Formatting Score: {formatting_score}%
            """

    prompt = f"""
        You are an AI resume reviewer for free-tier users.

        You receive the original resume plus structured outputs from earlier pipeline agents.
        Produce general, practical feedback only — not deep career counseling.

        === RESUME TEXT ===
        {resume_text}

        === USER GOAL (raw input) ===
        {user_goal}

        === AGENT 1 — INTENT & GOALS ===
        Target role: {target_role}
        Seniority: {seniority_level}
        Industry: {industry}
        Priority goals: {_json_block(priority_goals)}
        Focus areas: {_json_block(focus_areas)}
        Top keywords: {_json_block(top_keywords)}
        Optimization strategy: {_json_block(optimization_strategy)}

        === AGENT 2 — STRUCTURE SIGNALS ===
        Estimated years of experience: {years_exp}
        Section presence: {_json_block(section_flags)}
        {jd_scores_block}
        === INSTRUCTIONS ===
        - Free-tier only: keep feedback general; do NOT over-personalize
        - Use Agent 1 for light direction (role, goals, focus areas, keywords, avoid list)
        - Use Agent 2 for skills, sections, and JD gaps (only when JD data is present)
        - Use Agent 3 scores as the main quality signals
        - Ground every claim in the resume and the structured fields above
        - Do NOT invent skills, jobs, metrics, or achievements
        - Do NOT assume more about the candidate than the inputs support
        - Focus on:
        1. Overall resume quality (Overall Resume Score)
        2. Skills section (detected skills; include JD gaps only if JD was provided)
        3. Experience section (impact/clarity); if no experience section, use projects or other relevant sections
        4. Structure and readability (section flags + Necessary Sections / Summary / Formatting scores)
        - Keep suggestions simple, actionable, and few
        - Align light guidance with priority_goals / focus_areas / avoid when useful

        === OUTPUT FORMAT ===
        Return ONLY valid JSON (no markdown fences):
        {{
        "summary": "",
        "skills_feedback": "",
        "experience_feedback": "",
        "structure_feedback": "",
        "simple_suggestions": []
        }}

        Rules for fields:
        - summary: short overall take using the main scores and Agent 1 target role when available
        - skills_feedback: clarity/completeness of skills; mention gaps only if JD data exists
        - experience_feedback: impact and clarity of experience/projects
        - structure_feedback: sections, readability, metrics usage
        - simple_suggestions: max 5 short, practical bullets
        """

    response = await llm_call(prompt)

    logger.info(f"Agent 6: Finalizer agent response: {response}")

    return safe_parse(response, "finalizer_agent_free_tier")
