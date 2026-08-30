import logging
from typing import Optional

from app.helpers.llm_call import llm_call, safe_parse

logger = logging.getLogger(__name__)


async def intent_goal_agent(resume_text, jd_text: Optional[str] = "", user_goal: Optional[str] = ""):
    if jd_text == "":
        jd_text = "No job description provided."
    if user_goal == "":
        user_goal = "No specific goal provided."
    prompt = f"""
    You are an expert career advisor.

    Your task is to analyze the user's resume and optional job description, and extract structured intent and optimization goals.

    Return ONLY valid JSON.

    INPUT:
    Resume:
    {resume_text}

    Job Description:
    {jd_text}

    User Goal:
    {user_goal}

    OUTPUT FORMAT (strict):
    {{
    "target_role": "",
    "seniority_level": "",
    "industry": "", Example: "tech", "it", "business", "marketing", "sales", "finance", "customer service", "business development", "strategic planning", "negotiation", "supply chain management", "human resources", "hr", etc.
    "priority_goals": [],
    "focus_areas": [],
    "top_keywords": [],
    "optimization_strategy": {{
        "must_have": [],
        "nice_to_have": [],
        "avoid": []
    }}
    }}

    RULES:
    - Infer target_role primarily from Job Description if available, otherwise from Resume or User Goal
    - seniority_level must be one of: ["Intern", "Junior", "Mid", "Senior"]
    - focus_areas must be chosen from: ["experience", "projects", "skills", "education"]
    - top_keywords must be based on Job Description if provided, otherwise inferred from role
    - Limit:
    - top_keywords: max 8
    - priority_goals: max 5
    - optimization_strategy.must_have = critical skills from JD
    - optimization_strategy.nice_to_have = optional or secondary skills
    - optimization_strategy.avoid = common resume mistakes (e.g., "generic wording", "no metrics")
    - Be realistic. Do NOT invent experience or skills not present or implied.

    Return ONLY JSON.
    """

    response = await llm_call(prompt)

    return safe_parse(response, agent_name="intent_goal_agent")
