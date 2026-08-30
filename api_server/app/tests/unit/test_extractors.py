import pytest
from app.services.resume_analyzer import extract_certifications, extract_languages, extract_professional_links

CERTIFICATIONS_TEXT_SAMPLE = """
Certifications:
- AWS Certified Cloud Practitioner
"""

LANGUAGES_TEXT_SAMPLE = """
Languages:
• English                                        Native or Bilingual Proficiency
- Spanish\t\t Full Professional Proficiency
+ French - Fluent
Vietnamese\tBasic Proficiency
* German - Advanced Proficiency
"""

PROFESSIONAL_LINKS_TEXT_SAMPLE = """
Professional Links:
- https://www.linkedin.com/in/john-doe-1234567890
- https://github.com/john-doe
- https://gitlab.com/john-doe
- https://portfolio.john-doe.com
"""

def test_extract_certifications():
    certifications = extract_certifications(CERTIFICATIONS_TEXT_SAMPLE)
    assert certifications == ["AWS Certified Cloud Practitioner"]

def test_extract_languages():
    languages = extract_languages(LANGUAGES_TEXT_SAMPLE)
    assert languages == [{"language": "English", "proficiency": "native"},
                        {"language": "Spanish", "proficiency": "full professional"},
                        {"language": "French", "proficiency": "fluent"},
                        {"language": "Vietnamese", "proficiency": "basic"},
                        {"language": "German", "proficiency": "advanced"}]

def test_extract_professional_links():
    professional_links = extract_professional_links(PROFESSIONAL_LINKS_TEXT_SAMPLE)
    assert professional_links == {"linkedin": "https://www.linkedin.com/in/john-doe-1234567890", 
                                    "github": "https://github.com/john-doe", 
                                    "gitlab": "https://gitlab.com/john-doe", 
                                    "portfolio": "https://portfolio.john-doe.com", 
                                    "other": []}