# Extract skills from job description text

import sys
import os
from typing import List
from internal_db.skills import it_skills, business_skills
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def extract_skills_from_jd_text(jd_text: str) -> List[str]:
    found_skills = set()
    for skill in it_skills + business_skills:
        if skill.lower() in jd_text.lower():
            found_skills.add(skill)
    return list(found_skills)