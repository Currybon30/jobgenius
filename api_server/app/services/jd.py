# Extract skills from job description text

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from typing import List
from api_server.app.internal_db.skills import IT_SKILL_NORMALIZATION, BUSINESS_SKILL_NORMALIZATION
from app.helpers.resume_helpers import normalize_text, match_variants

def extract_skills_from_jd_text(jd_text: str) -> List[str]:
    jd_text = normalize_text(jd_text)
    all_skills = {**IT_SKILL_NORMALIZATION, **BUSINESS_SKILL_NORMALIZATION}
    
    found_skills = {
        canonical for canonical, variants in all_skills.items()
        if match_variants(jd_text, variants)
    }
    
    return list(found_skills)