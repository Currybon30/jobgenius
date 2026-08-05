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
