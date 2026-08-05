from app.services.resume_analyzer import has_metrics


def ats_agent_free_tier(agent2_result: dict):
    """
    Calculate the resume quality score for free tier users.
    Total score: 1.0
    Args:
        agent2_result: The result of the agent2 analyzer.
    Returns:
        A tuple containing the resume quality score (0.0 - 100.0), the necessary sections score (0.0 - 100.0), and the metrics score (0.0 - 1.0).
    """
    # Resume score distribution
    # 20% - Required Sections
    # 20% - Metrics
    # 30% - Experience/Projects
    # 15% - Skills Quality
    # 10% - Summary Quality
    # 5% - Formatting

    resume_score = 0
    section_score = 0
    experience_projects_score = 0
    skills_quality_score = 0
    summary_quality_score = 0
    formatting_score = 0
    results = {}

    # -------------------------
    # 1. Required Sections (20%)
    # -------------------------
    section_weight = {
        "skills": 0.25,
        "experience": 0.35,
        "projects": 0.35, # it won't be used, if experience is present
        "education": 0.20,
        "summary": 0.10,
        "contact_info": 0.10,
    }

    if agent2_result["has_skills"]:
        section_score += section_weight["skills"]
    
    if agent2_result["has_experience"]:
        section_score += section_weight["experience"]
    elif agent2_result["has_projects"]:
        section_score += section_weight["projects"]
    
    if agent2_result["has_education"]:
        section_score += section_weight["education"]
    
    if agent2_result["years_exp"] >= 3:
        section_score += section_weight["summary"] if agent2_result["has_summary"] else 0
    else:
        section_score += section_weight["summary"] if agent2_result["has_summary"] else 0.3 * section_weight["summary"]
    
    if agent2_result["emails"] or agent2_result["phone_numbers"]:
        section_score += section_weight["contact_info"]

    section_score = min(section_score, 1.0) # ensure the section score is not greater than 1.0
    resume_score = section_score * 0.2

    # -------------------------
    # 2. Metrics (20%)
    # -------------------------
    metrics_score = has_metrics(agent2_result["resume_text"])
    resume_score += metrics_score * 0.20

    # ------------------------------------
    # 3. Experience/Projects Quality (30%)
    # ------------------------------------
    if agent2_result["has_experience"]:
        experience_projects_score = 1.0
    elif agent2_result["has_projects"]:
        experience_projects_score = 0.75

    years_exp = agent2_result["years_exp"]

    if years_exp >= 5:
        experience_projects_score = min(experience_projects_score + 0.2, 1.0)
    elif years_exp >= 2:
        experience_projects_score = min(experience_projects_score + 0.1, 1.0)
    else:
        experience_projects_score = min(experience_projects_score + 0.05, 1.0)

    resume_score += experience_projects_score * 0.30

    # -------------------------
    # 4. Skills Quality (15%)
    # -------------------------
    hard_skills_score = 0
    if agent2_result.get("hard_skills"):
        num_hard_skills = len(agent2_result["hard_skills"])

        if num_hard_skills >= 10:
            hard_skills_score = 1.0
        elif num_hard_skills >= 5:
            hard_skills_score = 0.75
        else:
            hard_skills_score = 0.50

    skills_quality_score = hard_skills_score * 0.8 # For hard skills

    soft_skills_score = 0
    if agent2_result.get("soft_skills"):
        num_soft_skills = len(agent2_result["soft_skills"])

        if num_soft_skills >= 7:
            soft_skills_score = 1.0
        elif num_soft_skills >= 4:
            soft_skills_score = 0.75
        else:
            soft_skills_score = 0.50

    skills_quality_score += soft_skills_score * 0.2 # For soft skills
    resume_score += skills_quality_score * 0.15

    # -------------------------
    # 5. Summary Quality (10%)
    # -------------------------
    if agent2_result["has_summary"]:
        summary_quality_score = 1.0
    else:
        summary_quality_score = 0.35

    resume_score += summary_quality_score * 0.10

    # -------------------------
    # 6. Formatting (5%) - Free tier users don't have over formatting features check
    # -------------------------
    formatting_score = 1.0
    resume_score += formatting_score * 0.05

    results["resume_score"] = resume_score
    results["section_score"] = section_score
    results["experience_projects_score"] = experience_projects_score
    results["skills_quality_score"] = skills_quality_score
    results["summary_quality_score"] = summary_quality_score
    results["formatting_score"] = formatting_score
    

    ats_score = 0
    if agent2_result["jd_provided"]:
        hard_skills_score = agent2_result["matching_hard_skills_score"]
        soft_skills_score = agent2_result["matching_soft_skills_score"]

        ats_score = (
            0.5 * hard_skills_score +
            0.15 * soft_skills_score +
            0.25 * experience_projects_score +
            0.10 * resume_score 
        )

        results["ats_score"] = round(ats_score * 100, 2)
        results["hard_skills_score"] = round(hard_skills_score * 100, 2)
        results["soft_skills_score"] = round(soft_skills_score * 100, 2)

    return results
