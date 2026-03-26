import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from app.helpers.llm_call import llm_call, safe_parse

async def intent_goal_agent(resume_text, jd_text = None, user_goal = None):
    if jd_text is None or jd_text == "":
        jd_text = "No job description provided."
    if user_goal is None or user_goal == "":
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
    "industry": "",
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



########################### TESTING ###########################
if __name__ == "__main__":
    import asyncio
    import json

    sample_resume = """
    John Doe
    Software Engineer with 5 years of experience in web development, specializing in Python and JavaScript. 
    Worked at TechCorp from 2018 to 2023, leading a team of developers on various projects including an e-commerce platform and a real-time analytics dashboard. 
    Holds a B.S. in Computer Science from State University.
    """

    sample_jd = """
    We are looking for a Senior Software Engineer to join our team. The ideal candidate will have experience with Python, JavaScript, and cloud technologies. 
    Responsibilities include developing scalable web applications, collaborating with cross-functional teams, and mentoring junior developers.
    """

    sample_user_goal = "I want to transition into a senior role in the tech industry."

    result = asyncio.run(intent_goal_agent(sample_resume, sample_jd, sample_user_goal))
    print(json.dumps(result, indent=2))
    