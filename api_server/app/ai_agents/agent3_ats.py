from app.helpers.resume_helper import extract_section_content
import re
# Optional sections like certifications, languages detected in the resume is a plus
def has_metrics(text:str):
    # Check for presence of numbers that could indicate metrics in the experience section and/or projects section
    sections = extract_section_content(text)
    experience_text = sections.get("experience", "")
    projects_text = sections.get("projects", "")
    # Look for patterns including numbers, %, $, etc. in experience and projects sections
    metrics_pattern = r'(\d+[\w%$]*)'
    # Make sure every bullet point has some metrics
    experience_bullets = re.split(r'[\r\n]+', experience_text)
    projects_bullets = re.split(r'[\r\n]+', projects_text)
    experience_metrics = sum(bool(re.search(metrics_pattern, bullet)) for bullet in experience_bullets)
    projects_metrics = sum(bool(re.search(metrics_pattern, bullet)) for bullet in projects_bullets)
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
        return 0.1


def has_certifications(text:str):
    # Check for presence of certifications section or keywords like "certified", "certification", "course", "training"
    sections = extract_section_content(text)
    certifications_text = sections.get("certifications", "")
    if certifications_text:
        return 0.5
    return 0.1

def has_languages(text:str):
    # Check for presence of languages section or keywords like "language skills", "languages"
    sections = extract_section_content(text)
    languages_text = sections.get("languages", "")
    if languages_text:
        return 0.5
    return 0.1