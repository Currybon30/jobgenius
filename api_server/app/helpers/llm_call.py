import asyncio
import json
import logging
import re

from app.core.ollama_config import get_ollama_client

logger = logging.getLogger(__name__)


async def llm_call(prompt: str):
    try:
        client = get_ollama_client()
        response = await client.ainvoke(prompt)
        return response.response
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
