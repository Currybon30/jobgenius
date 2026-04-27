from ollama import AsyncClient
from app.core.config import settings
import asyncio
import json
import re
import logging


client = AsyncClient(settings.OLLAMA_HOST)
logger = logging.getLogger(__name__)

async def llm_call(prompt: str):
    try:
        response = await asyncio.wait_for(
            client.generate(
                model=settings.AI_MODEL_NAME, 
                prompt=prompt,
                options={"temperature": 0.2}),
            timeout=20
        )
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
        response = re.sub(r"^```[a-zA-Z]*\n?", "", response)  # remove opening ```json
        response = re.sub(r"\n?```$", "", response)           # remove closing ```
        
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