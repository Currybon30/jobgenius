import pymupdf
from fastapi import UploadFile
from app.internal_db.skills import SOFT_SKILL_NORMALIZATION, IT_SKILL_NORMALIZATION, BUSINESS_SKILL_NORMALIZATION
from app.ai_agents.agent3_ats import has_metrics
from app.helpers.resume_helper import extract_section_content
from app.services.jd import extract_skills_from_jd_text
from app.helpers.resume_helper import normalize_text, match_variants
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def extract_text_from_resume(resume_pdf_file: UploadFile) -> str:
    try:
        if not resume_pdf_file.filename or not resume_pdf_file.filename.lower().endswith('.pdf'):
            raise ValueError("Unsupported file format. Please upload a PDF.")
        file_bytes = await resume_pdf_file.read()
        if not file_bytes:
            raise ValueError("Uploaded PDF is empty.")

        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except FileNotFoundError as e:
        logger.error(f"File not found: {resume_pdf_file.filename}")
        raise e
    except ValueError as e:
        logger.error(f"Unsupported file format: {resume_pdf_file.filename}")
        raise e
    except Exception as e:
        logger.error(f"Error extracting text from resume: {e}")
        raise e
    
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
    if field == 'it' or field == 'technology' or field == 'software' or field == 'tech':
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
    matching_skills_score = len(found_skills) / len(jd_skills) if jd_skills else 0.1
    return {
        "skills": list(found_skills),
        "missing_skills": list(missing_skills)[:5],  # Limit to top 5 missing skills for free users
        "matching_skills_score": matching_skills_score,
        "soft_skills": list(found_soft_skills)
    }
    

def has_summary(text: str):
    summary_pattern = r'^\s*(summary|objective|profile|professional summary|career objective|professional objective|summary of qualification)\b'
    return re.search(summary_pattern, text, re.IGNORECASE | re.MULTILINE) is not None

def estimate_experience_years(text: str):
    total_years = 0
    current_year = datetime.now().year

    # Match: 2020 - 2023 OR 2021 - Present
    date_ranges = re.findall(r'(20\d{2})\s*[-–—]\s*(20\d{2}|present)', text, re.IGNORECASE)

    for start, end in date_ranges:
        start = int(start)
        end = current_year if end.lower() == "present" else int(end)

        if end >= start:
            total_years += (end - start)

    # Fallback: "3+ years"
    explicit = re.search(r'(\d+)\+?\s+years', text, re.IGNORECASE)
    if explicit:
        total_years = max(total_years, int(explicit.group(1)))

    return total_years


def estimate_experience_years_from_sections(sections: dict):
    # ✅ prioritize real experience
    text = sections.get("experience", "")
    if not text:
        return 0
    return estimate_experience_years(text)

    
    
def calculate_resume_quality_score_for_free_tier(text: str, jd_provided: bool, jd_text: str = ""):
    score = 0
    sections = extract_section_content(text)
    years_exp = estimate_experience_years_from_sections(sections)
    summary_present = has_summary(text)
    
    # -------------------------
    # 1. Sections (0.5)
    # -------------------------
    section_score = 0 
    if "skills" in sections:
        section_score += 0.5
    if "education" in sections:
        section_score += 0.5

    score += 0.5 * section_score
    
    # -------------------------
    # 2. Experience presence (0.1)
    # -------------------------
    if "experience" in sections:
        score += 0.1
        section_score += 0.5
    elif "projects" in sections:
        score += 0.07
        section_score += 0.3
        
        
    # -------------------------
    # 3. Summary (0.1)
    # -------------------------
    if years_exp >= 3:
        score += 0.1 if summary_present else 0
        section_score += 0.5 if summary_present else 0
    else:
        score += 0.1 if summary_present else 0.03
        section_score += 0.5 if summary_present else 0.3

    # -------------------------
    # 4. Basic metrics (0.1)
    # -------------------------
    metrics_score = has_metrics(text)
    score += 0.1 * metrics_score
    
    # -------------------------
    # 5. Contact info (0.2)
    # -------------------------
    contact_info = extract_contact_info(text)
    if contact_info["emails"] and contact_info["phone_numbers"]:
        score += 0.2
    
       
    if jd_provided:
        skills_info = extract_skills_from_text_with_jd(text, jd_text)
        score = 0.3 * score + 0.7 * skills_info["matching_skills_score"]

    # Keep the historical "section_score - 1.0" intent, but make it stable (0..1) before converting to percent.
    necessary_sections_score = max(0.0, min(1.0, section_score - 1.0))
    return round(score, 3) * 100, round(necessary_sections_score, 3) * 100, metrics_score

############################ Advanced features using AI #########################################