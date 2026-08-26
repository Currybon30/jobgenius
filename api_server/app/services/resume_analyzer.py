import logging
import re
from datetime import datetime

import pymupdf
from app.helpers.resume_helper import match_variants, normalize_text
from app.internal_db.skills import (BUSINESS_SKILL_NORMALIZATION,
                                    IT_SKILL_NORMALIZATION,
                                    SOFT_SKILL_NORMALIZATION)
from app.services.jd import extract_skills_from_jd_text
from fastapi import UploadFile

logger = logging.getLogger(__name__)

############################### EXTRACT SECTIONS ################################
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
            text += page.get_text() # type: ignore
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


def __extract_soft_skills_from_text(text: str):
    text = normalize_text(text)
    found_soft_skills = {
        canonical for canonical, variants in SOFT_SKILL_NORMALIZATION.items()
        if match_variants(text, variants)
    }
    return list(found_soft_skills)


def extract_skills_from_text_without_jd(text: str, field: str):
    text = normalize_text(text)
    found_soft_skills = __extract_soft_skills_from_text(text)
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


def extract_skills_from_text_with_jd(text: str, jd_text: str, limit: int = 5):
    text = normalize_text(text)
    jd_text = normalize_text(jd_text)
    jd_skills = extract_skills_from_jd_text(jd_text)
    all_skills = {**IT_SKILL_NORMALIZATION, **BUSINESS_SKILL_NORMALIZATION}
    found_skills = {
        canonical for canonical, variants in all_skills.items()
        if match_variants(text, variants) and canonical in jd_skills
    }
    missing_skills = set(jd_skills) - found_skills
    matching_skills_score = len(found_skills) / \
        len(jd_skills) if jd_skills else 0.1

    found_soft_skills_from_jd = set(__extract_soft_skills_from_text(jd_text))
    found_soft_skills_from_resume = set(__extract_soft_skills_from_text(text))
    
    missing_soft_skills = found_soft_skills_from_jd - found_soft_skills_from_resume
    matching_soft_skills = found_soft_skills_from_jd & found_soft_skills_from_resume
    matching_soft_skills_score = len(matching_soft_skills) / len(found_soft_skills_from_jd) if found_soft_skills_from_jd else 0.1
    return {
        "skills": list(found_skills),
        # Limit to top 5 missing skills for free users
        "missing_skills": list(missing_skills)[:limit],
        "matching_skills_score": min(matching_skills_score, 1.0),
        "soft_skills_in_resume": list(found_soft_skills_from_resume),
        "missing_soft_skills": list(missing_soft_skills)[:limit],
        "matching_soft_skills_score": min(matching_soft_skills_score, 1.0),
    }


def extract_sections_from_text(text: str):
    text = re.sub(r'\r\n', '\n', text)
    section_patterns = {
        "summary": r'^\s*(summary|objective|profile|professional summary|career objective|professional objective|summary of qualification)\b',
        "skills": r'^\s*(skills|technical skills)\b',
        "education": r'^\s*(education|academic background)\b',
        "experience": r'^\s*(experience|work experience|employment history|professional experience)\b',
        "projects": r'^\s*(projects|project experience)\b',
        "certifications": r'^\s*(certifications|certification|courses|training|qualifications|credentials|licenses)\b',
        "languages": r'^\s*(languages|language skills)\b',
    }

    matches = []
    for section, pattern in section_patterns.items():
        for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
            matches.append((section, match.start()))

    matches.sort(key=lambda x: x[1])

    extracted = {}
    for i in range(len(matches)):
        section, start = matches[i]
        end = matches[i + 1][1] if i + 1 < len(matches) else len(text)

        content = text[start:end].strip()

        # keep longest match if duplicate section appears
        if section not in extracted or len(content) > len(extracted[section]):
            extracted[section] = content

    return extracted

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

############################### RULE-BASED ANALYSIS ################################
def __estimate_experience_years(text: str):
    total_years = 0
    current_year = datetime.now().year

    # Match: 2020 - 2023 OR 2021 - Present
    date_ranges = re.findall(
        r'(20\d{2})\s*[-–—]\s*(20\d{2}|present)', text, re.IGNORECASE)

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
    return __estimate_experience_years(text)


# Optional sections like certifications, languages detected in the resume is a plus
def has_metrics(text: str):
    # Check for presence of numbers that could indicate metrics in the experience section and/or projects section
    sections = extract_sections_from_text(text)
    experience_text = sections.get("experience", "")
    projects_text = sections.get("projects", "")
    # Look for patterns including numbers, %, $, etc. in experience and projects sections
    metrics_pattern = r'(\d+[\w%$]*)'
    # Make sure every bullet point has some metrics
    experience_bullets = [
        b for b in re.split(r'[\r\n]+', experience_text) if b.strip()
    ]
    projects_bullets = [
        b for b in re.split(r'[\r\n]+', projects_text) if b.strip()
    ]
    experience_metrics = sum(
        bool(re.search(metrics_pattern, bullet)) for bullet in experience_bullets
    )
    projects_metrics = sum(
        bool(re.search(metrics_pattern, bullet)) for bullet in projects_bullets
    )
    total_bullets = len(experience_bullets) + len(projects_bullets)
    if total_bullets == 0:
        return 0.0
    metrics_ratio = (experience_metrics + projects_metrics) / total_bullets
    if metrics_ratio >= 0.7:
        return 1.0
    elif metrics_ratio >= 0.5:
        return 0.7
    elif metrics_ratio >= 0.3:
        return 0.4
    else:
        return 0.0