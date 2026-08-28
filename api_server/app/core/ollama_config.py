from app.core.config import settings
from langchain_ollama import OllamaLLM, OllamaEmbeddings
import logging

logger = logging.getLogger(__name__)
ollama_client = None
ollama_embedding_model = None

async def init_ollama():
    global ollama_client, ollama_embedding_model
    if ollama_client is None:
        ollama_client = OllamaLLM(
            model=settings.OLLAMA_MODEL,
            temperature=0.5,
            base_url=settings.OLLAMA_HOST,
        )
    if ollama_embedding_model is None:
        ollama_embedding_model = OllamaEmbeddings(
            model=settings.EMBEDDING_MODEL,
            base_url=settings.OLLAMA_HOST,
        )
    logger.info("Ollama client and embedding model initialized")

async def close_ollama():
    global ollama_client, ollama_embedding_model

    if ollama_client is not None:
        ollama_client = None
    if ollama_embedding_model is not None:
        ollama_embedding_model = None
    logger.info("Ollama client and embedding model closed successfully")

def get_ollama_client() -> OllamaLLM:
    if ollama_client is None:
        raise RuntimeError("Ollama client not initialized")
    return ollama_client

def get_ollama_embedding_model() -> OllamaEmbeddings:
    if ollama_embedding_model is None:
        raise RuntimeError("Ollama embedding model not initialized")
    return ollama_embedding_model