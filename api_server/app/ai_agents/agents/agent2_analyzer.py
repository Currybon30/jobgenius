from typing import Optional

from app.services.resume_analyzer import (
                    extract_skills_from_text_without_jd, 
                    extract_skills_from_text_with_jd, 
                    extract_sections_from_text,estimate_experience_years_from_sections, 
                    has_metrics, extract_contact_info, 
                    extract_skills_from_text_with_jd, extract_sections_from_text,
                    extract_certifications, extract_languages, extract_professional_links)

def analyzer_agent_free_tier(resume_text, industry: str = "", jd_text: Optional[str] = ""):
    """
    No languages and certifications are checked for now.
    """
    sections = extract_sections_from_text(resume_text)
    years_exp = estimate_experience_years_from_sections(sections)
    has_summary_bool = True if "summary" in sections else False
    has_skills_bool = True if "skills" in sections else False
    has_experience_bool = True if "experience" in sections else False
    has_projects_bool = True if "projects" in sections else False
    has_education_bool = True if "education" in sections else False
    contact_info = extract_contact_info(resume_text)
    skills_info = None
    has_metrics_bool = True if has_metrics(resume_text) > 0 else False

    if jd_text == "":
        skills_info = extract_skills_from_text_without_jd(resume_text, industry)
        return {
            "sections": sections,
            "years_exp": years_exp,
            "has_summary": has_summary_bool,
            "has_skills": has_skills_bool,
            "has_experience": has_experience_bool,
            "has_projects": has_projects_bool,
            "has_education": has_education_bool,
            "emails": contact_info["emails"],
            "phone_numbers": contact_info["phone_numbers"],
            "has_metrics": has_metrics_bool,
            "hard_skills": skills_info["skills"],
            "soft_skills": skills_info["soft_skills"]
        }
    else:
        skills_info = extract_skills_from_text_with_jd(resume_text, jd_text, limit=5)
        return {
            "sections": sections,
            "years_exp": years_exp,
            "has_summary": has_summary_bool,
            "has_skills": has_skills_bool,
            "has_experience": has_experience_bool,
            "has_projects": has_projects_bool,
            "has_education": has_education_bool,
            "emails": contact_info["emails"],
            "phone_numbers": contact_info["phone_numbers"],
            "has_metrics": has_metrics_bool,
            "hard_skills": skills_info["skills"],
            "soft_skills": skills_info["soft_skills_in_resume"],
            "missing_hard_skills": skills_info["missing_skills"],
            "matching_hard_skills_score": skills_info["matching_skills_score"],
            "missing_soft_skills": skills_info["missing_soft_skills"],
            "matching_soft_skills_score": skills_info["matching_soft_skills_score"]
        }

def analyzer_agent_premium(resume_text, industry: str = "", jd_text: Optional[str] = ""):
    """
    Premium users have access to all the features of the free tier, plus:
    - Certifications
    - Languages
    - Professional links
    - Volunteer section (a plus if no experience section and relevant to the resume title and/or job description)
    """
    results = {}
    analyzer_agent_free_tier_result = analyzer_agent_free_tier(resume_text, industry, jd_text)
    for key, value in analyzer_agent_free_tier_result.items():
        results[key] = value
    sections = extract_sections_from_text(resume_text)
    has_volunteer_bool = True if "volunteer" in sections else False
    results["certifications"] = extract_certifications(sections.get("certifications", ""))
    results["languages"] = extract_languages(sections.get("languages", ""))
    results["professional_links"] = extract_professional_links(resume_text)
    if results["has_experience"] == False and results["has_projects"] == False and has_volunteer_bool:
        results["has_volunteer"] = True
    else:
        results["has_volunteer"] = False
    return results