import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import pymupdf
from internal_db.skills import SOFT_SKILL_NORMALIZATION, IT_SKILL_NORMALIZATION, BUSINESS_SKILL_NORMALIZATION
from jd import extract_skills_from_jd_text
from app.config import AI_MODEL_NAME, OLLAMA_HOST
from app.helpers.resume_helpers import normalize_text, match_variants
import re


def extract_text_from_resume(file_path: str):
    try:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return "File not found."
        if not file_path.lower().endswith('.pdf'):
            print(f"Unsupported file format: {file_path}")
            return "Unsupported file format. Please upload a PDF."
        doc = pymupdf.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error extracting text from resume: {e}")
        return ""
    
    
def extract_contact_info(text: str):
    # Use regex to find potential email addresses and phone numbers
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
    
    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)
    
    return {
        "emails": emails,
        "phone_numbers": phones
    }
    
def extract_soft_skills_from_text(text: str):
    text = normalize_text(text)
    found_soft_skills = {
        canonical for canonical, variants in SOFT_SKILL_NORMALIZATION.items()
        if match_variants(text, variants)
    }
    return list(found_soft_skills)
    
    
def extract_skills_from_text_without_jd(text: str, field: str):
    text = normalize_text(text)
    found_soft_skills = extract_soft_skills_from_text(text)
    if field == 'it':
        skills_to_check = IT_SKILL_NORMALIZATION
    elif field == 'business':
        skills_to_check = BUSINESS_SKILL_NORMALIZATION
    else:
        return {"skills": [], "soft_skills": found_soft_skills}
    
    found_skills = {
        canonical for canonical, variants in skills_to_check.items()
        if match_variants(text, variants)
    }
            
    return {
        "skills": list(found_skills),
        "soft_skills": list(found_soft_skills),
    }
    

def extract_skills_from_text_with_jd(text: str, jd_text: str):
    text = normalize_text(text)
    jd_skills = extract_skills_from_jd_text(jd_text)
    found_soft_skills = extract_soft_skills_from_text(text)
    all_skills = {**IT_SKILL_NORMALIZATION, **BUSINESS_SKILL_NORMALIZATION}
    found_skills = {
        canonical for canonical, variants in all_skills.items()
        if match_variants(text, variants) and canonical in jd_skills
    }
    missing_skills = set(jd_skills) - found_skills
    matching_score = len(found_skills) / len(jd_skills) * 100 if jd_skills else 0
    return {
        "skills": list(found_skills),
        "missing_skills": list(missing_skills)[:5],  # Limit to top 5 missing skills for free users
        "matching_score": round(matching_score, 2),
        "soft_skills": list(found_soft_skills)
    }

############################ Advanced features using AI #########################################
# Apply AI for smarter keyword extraction from PDF, semantic similarity, resume feedback.
# Use AI agentic approach

    
    

############################ TESTING #########################################
from resume_ai_feedback import resume_feedback_free_tier
import asyncio
if __name__ == "__main__":
    pdf_path = r"D:\IT\My Projects\job_recommender_system\api_server\external_resources\Tuong Nguyen Pham Resume.pdf"
    resume_text = extract_text_from_resume(pdf_path)
    
    skills = extract_skills_from_text_without_jd(resume_text, 'it')

    skills = skills['skills'] + skills['soft_skills']

    resume_feedback = asyncio.run(resume_feedback_free_tier(resume_text, skills))
    print("AI Resume Feedback:", resume_feedback)