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
    jd_text: Optional[str] = "",
    user_goal: Optional[str] = "",
):
    """
    Agent 6 — final free-tier feedback.

    Args:
        resume_text: Original resume text.
        intent: Agent 1 output (target role, goals, keywords, strategy).
        analyzer: Agent 2 output (sections, skills, JD match fields if any).
        ats: Agent 3 output (resume quality / ATS scores).
        jd_text: The text of the job description.
        user_goal: The original user goal string.
    """
    intent = intent or {}
    analyzer = analyzer or {}
    ats = ats or {}

    if user_goal == "":
        user_goal = "No specific goal provided."
    if jd_text == "":
        jd_text = "No job description provided."

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

    if jd_text != "No job description provided.":
        jd_scores_block = f"""
            === AGENT 2 — JD SKILL MATCH ===
            Hard skills on resume: {_json_block(hard_skills)}
            Soft skills on resume: {_json_block(soft_skills)}
            Missing hard skills (in JD, not on resume): {_json_block(missing_hard_skills)}
            Missing soft skills (in JD, not on resume): {_json_block(missing_soft_skills)}
            Matching hard skills score: {matching_hard_skills_score}%
            Matching soft skills score: {matching_soft_skills_score}%

            Job description (reference only; do not quote at length):
            {jd_text}

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
        - If the resume does not have clear headings for sections, do not say something like "You only have 0 years of experience" (If they actually have experience, they will have a section for it). Instead, say something like "You should add a section for your experience".

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

    if response:
        logger.info("Agent 6: Finalizer agent response received")
    return safe_parse(response, "finalizer_agent_free_tier")


async def finalizer_agent_premium(
    resume_text: str,
    intent: dict,
    analyzer: dict,
    ats: dict,
    optimizer: dict,
    jd_text: Optional[str] = "",
    user_goal: Optional[str] = "",
):
    """
    Agent 6 — final premium feedback.

    Args:
        resume_text: Original resume text.
        intent: Agent 1 output (target role, goals, keywords, strategy).
        analyzer: Agent 2 premium output (sections, skills, certifications, languages, links).
        ats: Agent 3 premium output (quality / ATS scores + bonus scores).
        optimizer: Agent 4 output (optimized resume and change notes).
        jd_text: The text of the job description.
        user_goal: The original user goal string.
    """
    intent = intent or {}
    analyzer = analyzer or {}
    ats = ats or {}
    optimizer = optimizer or {}

    if user_goal == "":
        user_goal = "No specific goal provided."
    if jd_text == "":
        jd_text = "No job description provided."

    target_role = intent.get("target_role", "")
    seniority_level = intent.get("seniority_level", "")
    industry = intent.get("industry", "")
    priority_goals = intent.get("priority_goals", [])
    focus_areas = intent.get("focus_areas", [])
    top_keywords = intent.get("top_keywords", [])
    optimization_strategy = intent.get("optimization_strategy", {})

    hard_skills = analyzer.get("hard_skills", [])
    soft_skills = analyzer.get("soft_skills", [])
    years_exp = analyzer.get("years_exp", 0)
    certifications = analyzer.get("certifications", [])
    languages = analyzer.get("languages", [])
    professional_links = analyzer.get("professional_links", [])
    section_flags = {
        "has_summary": analyzer.get("has_summary", False),
        "has_skills": analyzer.get("has_skills", False),
        "has_experience": analyzer.get("has_experience", False),
        "has_projects": analyzer.get("has_projects", False),
        "has_volunteer": analyzer.get("has_volunteer", False),
        "has_education": analyzer.get("has_education", False),
        "has_metrics": analyzer.get("has_metrics", False),
        "has_contact": bool(analyzer.get("emails") or analyzer.get("phone_numbers")),
    }

    missing_hard_skills = analyzer.get("missing_hard_skills", [])
    missing_soft_skills = analyzer.get("missing_soft_skills", [])
    matching_hard_skills_score = _pct(analyzer.get("matching_hard_skills_score", 0))
    matching_soft_skills_score = _pct(analyzer.get("matching_soft_skills_score", 0))

    resume_score = _pct(ats.get("resume_score", 0))
    section_score = _pct(ats.get("section_score", 0))
    experience_projects_score = _pct(ats.get("experience_projects_score", 0))
    skills_quality_score = _pct(ats.get("skills_quality_score", 0))
    summary_quality_score = _pct(ats.get("summary_quality_score", 0))
    formatting_score = _pct(ats.get("formatting_score", 0))
    ats_score = ats.get("ats_score")
    hard_match_ats = ats.get("hard_skills_score")
    soft_match_ats = ats.get("soft_skills_score")
    certifications_score = ats.get("certifications_score", 0)
    languages_score = ats.get("languages_score", 0)
    professional_links_score = ats.get("professional_links_score", 0)

    optimized_resume = optimizer.get("optimized_resume", "")
    optimized_sections = optimizer.get("optimized_sections", {})
    keywords_integrated = optimizer.get("keywords_integrated", [])
    changes_made = optimizer.get("changes_made", [])
    suggested_additions_if_true = optimizer.get("suggested_additions_if_true", [])
    optimization_notes = optimizer.get("optimization_notes", "")

    has_jd = jd_text != "No job description provided."
    score_dashboard = f"""
        Overall Resume: {resume_score}% | Sections: {section_score}% | Experience/Projects: {experience_projects_score}%
        Skills Quality: {skills_quality_score}% | Summary: {summary_quality_score}% | Formatting: {formatting_score}%
        ATS Fit: {ats_score if ats_score is not None else "N/A"}%
        Premium bonuses — Certifications: {certifications_score} | Languages: {languages_score} | Links: {professional_links_score}
        """

    if has_jd:
        jd_scores_block = f"""
            === AGENT 2 — JD SKILL MATCH (PREMIUM) ===
            Hard skills on resume: {_json_block(hard_skills)}
            Soft skills on resume: {_json_block(soft_skills)}
            Missing hard skills (in JD, not on resume): {_json_block(missing_hard_skills)}
            Missing soft skills (in JD, not on resume): {_json_block(missing_soft_skills)}
            Matching hard skills score: {matching_hard_skills_score}%
            Matching soft skills score: {matching_soft_skills_score}%

            Certifications detected: {_json_block(certifications)}
            Languages detected: {_json_block(languages)}
            Professional links detected: {_json_block(professional_links)}

            Job description (reference only; do not quote at length):
            {jd_text}

            === AGENT 3 — QUALITY & ATS SCORES (PREMIUM) ===
            {score_dashboard}
            - Hard Skills Match (ATS): {hard_match_ats if hard_match_ats is not None else "N/A"}%
            - Soft Skills Match (ATS): {soft_match_ats if soft_match_ats is not None else "N/A"}%
            """
    else:
        jd_scores_block = f"""
            === AGENT 2 — DETECTED PROFILE (no JD) ===
            Hard skills: {_json_block(hard_skills)}
            Soft skills: {_json_block(soft_skills)}
            Certifications detected: {_json_block(certifications)}
            Languages detected: {_json_block(languages)}
            Professional links detected: {_json_block(professional_links)}
            No job description — do NOT invent JD fit, missing skills, or matching scores.

            === AGENT 3 — QUALITY SCORES (PREMIUM) ===
            {score_dashboard}
            """

    jd_fit_instruction = (
        "- jd_fit_analysis: deep JD alignment — keyword gaps, ATS risk, and how to close gaps using true experience"
        if has_jd
        else "- jd_fit_analysis: empty string (no JD provided)"
    )

    prompt = f"""
        You are a senior career coach and executive resume strategist for PREMIUM users only.

        Free-tier users receive generic, surface-level tips (max 5 bullets, no optimizer, no interview prep).
        Your job is to deliver a white-glove, role-specific coaching report that feels worth paying for.

        You have:
        - The original resume
        - Full intent analysis (target role, seniority, industry, strategy)
        - Premium analyzer (certifications, languages, professional links, JD gaps)
        - Premium ATS scoring with bonus signals
        - An optimized resume draft from Agent 4 (before/after reference)

        === SCORE DASHBOARD ===
        {score_dashboard}

        === RESUME TEXT (ORIGINAL) ===
        {resume_text}

        === USER GOAL ===
        {user_goal}

        === AGENT 1 — INTENT & CAREER TARGET ===
        Target role: {target_role}
        Seniority: {seniority_level}
        Industry: {industry}
        Priority goals: {_json_block(priority_goals)}
        Focus areas: {_json_block(focus_areas)}
        Top keywords: {_json_block(top_keywords)}
        Optimization strategy: {_json_block(optimization_strategy)}

        === AGENT 2 — STRUCTURE & PREMIUM SIGNALS ===
        Estimated years of experience: {years_exp}
        Section presence: {_json_block(section_flags)}
        {jd_scores_block}

        === AGENT 4 — OPTIMIZED RESUME (BEFORE → AFTER) ===
        Optimization notes: {optimization_notes}
        Keywords integrated: {_json_block(keywords_integrated)}
        Changes made: {_json_block(changes_made)}
        Suggested additions (only if true): {_json_block(suggested_additions_if_true)}
        Optimized sections: {_json_block(optimized_sections)}
        Full optimized resume (reference; summarize improvements, do not paste verbatim):
        {optimized_resume}

        === PREMIUM COACHING RULES ===
        1. Write like a 1:1 career coach — confident, specific, encouraging, never generic.
        2. Anchor everything to target_role, seniority_level, industry, and user_goal.
        3. Use the score dashboard to prioritize what matters most (lowest scores = highest urgency).
        4. Compare ORIGINAL vs OPTIMIZED: call out what Agent 4 fixed and what still needs human action.
        5. Cover certifications, languages, and professional links — free tier cannot do this.
        6. Give interview-ready advice: talking points tied to real resume evidence.
        7. Include a recruiter_lens (6-second skim) AND competitive_positioning vs typical applicants.
        8. Ground every claim in provided data — never invent employers, skills, metrics, or credentials.
        9. If years_exp is 0 due to missing headings, recommend structure fixes — do not say "0 years experience".
        10. Be substantially deeper than free tier: more detail, more strategy, more actionable sequencing.
        11. A volunteer section, mention it as a plus.

        === OUTPUT FORMAT ===
        Return ONLY valid JSON (no markdown fences):
        {{
        "summary": "",
        "skills_feedback": "",
        "experience_feedback": "",
        "structure_feedback": "",
        "simple_suggestions": [],
        "strength_highlights": [],
        "growth_opportunities": [],
        "jd_fit_analysis": "",
        "certifications_feedback": "",
        "languages_feedback": "",
        "professional_links_feedback": "",
        "optimizer_review": "",
        "interview_talking_points": [],
        "priority_action_plan": [],
        "recruiter_lens": "",
        "competitive_positioning": ""
        }}

        Field rules:
        - summary: 3–5 sentence executive briefing — role fit, headline score, top win, top gap
        - skills_feedback: detailed skills/JD keyword strategy; mention integrated keywords from Agent 4
        - experience_feedback: bullet-level impact coaching; before/after emphasis from optimizer
        - structure_feedback: ATS, sections, formatting, scannability, links
        - simple_suggestions: max 5 quick wins (short bullets) for users who skim
        - strength_highlights: max 5 evidence-backed strengths for this target role
        - growth_opportunities: max 5 highest-leverage gaps (not generic advice)
        {jd_fit_instruction}
        - certifications_feedback: value and presentation of certs; gaps only if role-appropriate
        - languages_feedback: language assets and how to leverage them for the role/market
        - professional_links_feedback: LinkedIn/GitHub/portfolio presence and polish
        - optimizer_review: what Agent 4 improved, what still needs manual editing, suggested_additions_if_true
        - interview_talking_points: max 6 STAR-ready angles from real resume content
        - priority_action_plan: max 6 ordered steps ("Week 1: ...", "Before applying: ...") — sequenced roadmap
        - recruiter_lens: 2–3 sentences — how a recruiter reads this resume in a quick skim
        - competitive_positioning: 2–4 sentences — how this candidate stands out vs typical {target_role} applicants
        """

    response = await llm_call(prompt)
    if response:
        logger.info("Agent 6: Finalizer agent response received")

    return safe_parse(response, "finalizer_agent_premium")