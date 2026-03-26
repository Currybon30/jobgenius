import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from ollama import AsyncClient
from app.config import AI_MODEL_NAME, OLLAMA_HOST

async def resume_feedback_free_tier(resume_text, list_skills, jd_text = None, missing_skills = None, matching_score = 0, missing_skills_score = 0, metrics_score = 0, necessary_sections_score = 0):
    # list_skills is the list of skills including both hard and soft skills extracted from the resume
    # missing_skills is the list of skills that were not found in the resume
    # matching_score is the percentage of skills found in the resume
    # jd_text is the text of the job description
    # resume_text is the text of the resume
    #! For free tier users, we will provide basic feedback based on the skills found and missing, and the matching score.
    if jd_text is None or jd_text == "":
        prompt = f"""
            You are an AI resume reviewer.

            Analyze the resume and provide general feedback for free tier users.

            Resume:
            {resume_text}

            Detected Skills:
            {list_skills}

            Instructions:
            - Provide general feedback only (no deep or highly personalized analysis)
            - Do NOT assume too much about the candidate
            - Focus on:
            1. Overall resume quality
            2. Skills section (clarity and completeness)
            3. Experience section (impact, clarity)
            4. Structure and readability
            - Keep suggestions simple and useful

            Output format:
            - Summary
            - Skills Feedback
            - Experience Feedback
            - Structure Feedback
            - Simple Suggestions
            """
    else:
        prompt = f"""
            You are an AI resume reviewer.

            Analyze the resume and provide general feedback for free tier users.

            Resume:
            {resume_text}

            Detected Skills:
            {list_skills}
            
            Missing Skills:
            {missing_skills}
            
            Matching Score: {matching_score}% 
            + Missing Skills Score: {missing_skills_score}%
            + Metrics Score: {metrics_score}%
            + Necessary Sections Score: {necessary_sections_score}%

            Instructions:
            - Provide general feedback only (no deep or highly personalized analysis)
            - Do NOT assume too much about the candidate
            - Focus on:
            1. Overall resume quality
            2. Skills section (clarity and completeness)
            3. Experience section (impact, clarity) if no experience section is found, check for the presence of projects or other relevant sections that can demonstrate experience
            4. Structure and readability
            - Keep suggestions simple and useful

            Output format:
            - Summary
            - Skills Feedback
            - Experience Feedback
            - Structure Feedback
            - Simple Suggestions
            """
    
    
    
    response = await AsyncClient(host=OLLAMA_HOST).generate(model=AI_MODEL_NAME, prompt=prompt)
    return response.response

