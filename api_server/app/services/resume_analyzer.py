import os
import pymupdf
from app.internal_db.skills import SOFT_SKILL_NORMALIZATION, IT_SKILL_NORMALIZATION, BUSINESS_SKILL_NORMALIZATION
from app.services.jd import extract_skills_from_jd_text
from api_server.app.helpers.resume_helper import normalize_text, match_variants
import re
from datetime import datetime

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
    

def extract_section_content(text: str):
    text = re.sub(r'\r\n', '\n', text)
    section_patterns = {
        "summary": r'^\s*(summary|objective|profile|professional summary|professional objective|career objective)\b',
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

def has_summary(text: str):
    summary_pattern = r'^\s*(summary|objective|profile|professional summary|career objective|professional objective)\b'
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
    text = ""

    # ✅ prioritize real experience
    if "experience" in sections:
        text += sections["experience"]

    # ⚠️ fallback for juniors
    elif "projects" in sections:
        text += sections["projects"]

    return estimate_experience_years(text)

    
    
def calculate_resume_quality_score_for_free_tier(text: str, jd_provided: bool):
    score = 0
    sections = extract_section_content(text)
    years_exp = estimate_experience_years_from_sections(sections)
    
    # -------------------------
    # 1. Sections (0.2)
    # -------------------------
    section_score = 0
    if "skills" in sections:
        section_score += 0.5
    if "education" in sections:
        section_score += 0.5

    score += 0.2 * section_score
    
    # -------------------------
    # 2. Experience presence (0.1)
    # -------------------------
    if "experience" in sections:
        score += 0.1
    elif "projects" in sections:
        score += 0.07
        
    # -------------------------
    # 3. Summary (0.05)
    # -------------------------
    if years_exp >= 3:
        score += 0.05 if has_summary(text) else 0
    else:
        score += 0.05 if has_summary(text) else 0.03

    # -------------------------
    # 4. Basic metrics (0.05)
    # -------------------------
    exp_text = sections.get("experience", "") or sections.get("projects", "")
    bullets = [b.strip() for b in re.split(r'[\n•\-]', exp_text) if b.strip()]

    if bullets:
        metric_count = sum(
            bool(re.search(r'\d+%|\$\d+|\d+\s*(users|clients|x|times)', b, re.I))
            for b in bullets
        )
        ratio = metric_count / len(bullets)

        if ratio >= 0.5:
            score += 0.05
        elif ratio >= 0.3:
            score += 0.03
        elif ratio > 0:
            score += 0.01
            
    if jd_provided:
        # -------------------------
        # 5. Skills match (0.7)
        # -------------------------
        skills_info = extract_skills_from_text_with_jd(text, "")
        score = 0.3 * score + 0.7 * skills_info["matching_skills_score"]

    return round(score, 3) * 100 # Convert to percentage

############################ Advanced features using AI #########################################

    

############################ TESTING #########################################
if __name__ == "__main__":
    from app.ai_agents.agent6_finalizer import resume_feedback_free_tier
    import asyncio
    pdf_path = r"D:\IT\My Projects\job_recommender_system\api_server\external_resources\Tuong Nguyen Pham Resume.pdf"
    resume_text = extract_text_from_resume(pdf_path)
    
    skills = extract_skills_from_text_without_jd(resume_text, 'it')

    skills = skills['skills'] + skills['soft_skills']

    resume_feedback = asyncio.run(resume_feedback_free_tier(resume_text, skills))
    print("AI Resume Feedback:", resume_feedback)