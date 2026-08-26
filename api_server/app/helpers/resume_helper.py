import re
from typing import List
import logging
from app.models.resume import Resume


def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def match_variants(text: str, variants: List[str]) -> bool:
    for variant in variants:
        pattern = rf"\b{re.escape(variant.lower())}\b"
        if re.search(pattern, text):
            return True
    return False


def format_analyzer_result(result: dict):
    """
    Format the result of the multi-agents to a proper format before saving to the database (MongoDB)
    """
    pass


def analyzer_result_to_text(result: dict) -> str:
    """
    Convert the result of the multi-agents to a single meaningful text for job recommendation
    """
    pass