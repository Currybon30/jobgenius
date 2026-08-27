from app.core.config import settings
from ollama import AsyncClient
import logging

logger = logging.getLogger(__name__)
ollama_client = None

async def init_ollama():
    global ollama_client
    if ollama_client is None:
        ollama_client = AsyncClient(settings.OLLAMA_HOST)
        
    # Verify if the model is available
    await ollama_client.list()
    logger.info(f"Ollama client initialized successfully")

async def close_ollama():
    global ollama_client

    if ollama_client is not None:
        del ollama_client

def get_ollama_client() -> AsyncClient:
    if ollama_client is None:
        raise RuntimeError("Ollama client not initialized")
    return ollama_client