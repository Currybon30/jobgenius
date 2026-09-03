import asyncio
import json
import logging
import re
from typing import Any
import codecs

from app.core.config import settings
from langchain_ollama import OllamaLLM

logger = logging.getLogger(__name__)


async def llm_call(prompt: str):
    try:
        client = OllamaLLM(
            model=settings.OLLAMA_MODEL,
            temperature=0.5,
            base_url=settings.OLLAMA_HOST,
        )
        response = await client.ainvoke(prompt)
        return response
    except asyncio.TimeoutError:
        logger.error("[ERROR] LLM call timed out")
        return ""
    except Exception as e:
        logger.error(f"[ERROR] LLM call failed: {e}")
        return ""


def safe_parse(response: str, agent_name="unknown"):
    if not response or not isinstance(response, str):
        return {
            "error": "Empty or invalid response",
            "agent": agent_name,
            "raw": response
        }

    response = response.strip()

    if response.startswith("```"):
        # remove opening ```json
        response = re.sub(r"^```[a-zA-Z]*\n?", "", response)
        # remove closing ```
        response = re.sub(r"\n?```$", "", response)

    # 1. Direct parse
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    # 2. Extract multiple JSON candidates (non-greedy)
    try:
        matches = re.findall(r"\{.*?\}", response, re.DOTALL)
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
    except Exception:
        pass

    # 3. Attempt quick fixes (very useful)
    try:
        fixed = response.replace("'", '"')
        fixed = re.sub(r",\s*}", "}", fixed)
        return json.loads(fixed)
    except Exception:
        pass

    # 4. Final fallback
    logger.error(f"[ERROR] {agent_name} returned invalid JSON")

    return {
        "error": "Invalid JSON",
        "agent": agent_name,
        "raw": response
    }


def _normalize_jobfinder_jobs(raw_jobs: Any) -> list[dict]:
    """Accept MCP / JSearch / JSON string shapes → list of job dicts."""
    if not raw_jobs:
        logger.error("[ERROR] agent7_jobfinder: returned no jobs")
        return []

    # Already a list of JSearch jobs
    if isinstance(raw_jobs, list) and raw_jobs:
        first = raw_jobs[0]
        if isinstance(first, dict) and "job_id" in first:
            return raw_jobs

        # LangChain MCP: [{"type": "text", "text": "<json>"}]
        if isinstance(first, dict) and "text" in first:
            text = first["text"]
            parsed = json.loads(text) if isinstance(text, str) else text
            if isinstance(parsed, list):
                return parsed
            if isinstance(parsed, dict):
                return [parsed]
            return []

    # Single JSON string
    if isinstance(raw_jobs, str):
        parsed = json.loads(raw_jobs)
        return parsed if isinstance(parsed, list) else [parsed]

    # Single job dict
    if isinstance(raw_jobs, dict):
        return [raw_jobs]

    return []


def _last_assistant_content(messages: list) -> str:
    if not messages:
        return ""
    last = messages[-1]
    if isinstance(last, dict):
        content = last.get("content", "")
    else:
        content = getattr(last, "content", "")
    returned_content = content if isinstance(content, str) else str(content)
    returned_content = codecs.decode(returned_content, "unicode_escape")
    return returned_content


def agent7_jobfinder_format_result(messages: list[dict[str, Any]], raw_jobs: list[dict[str, Any]]):
    try:
        formatted_message = _last_assistant_content(messages)
        formatted_jobs = _normalize_jobfinder_jobs(raw_jobs)
        if not formatted_jobs:
            return {
                "message": formatted_message,
                "jobs": [],
                "error": "No jobs found"
            }
        else:
            return {
                "message": formatted_message,
                "jobs": formatted_jobs
            }
    except Exception as e:
        logger.error(f"[ERROR] Failed to format agent7 jobfinder result: {e}")
        return {
            "message": _last_assistant_content(messages) or "Job search completed with formatting error.",
            "jobs": [],
            "error": str(e),
        }
