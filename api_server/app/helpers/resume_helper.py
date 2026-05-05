import re
from typing import List


def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def match_variants(text: str, variants: List[str]) -> bool:
    for variant in variants:
        pattern = rf"\b{re.escape(variant.lower())}\b"
        if re.search(pattern, text):
            return True
    return False


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
