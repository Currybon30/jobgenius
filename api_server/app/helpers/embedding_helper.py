from app.core.config import settings
from app.core.ollama_config import get_ollama_client


async def embed_text(text: str) -> list[float]:
    ollama_client = get_ollama_client()
    response = await ollama_client.embed(
        model=settings.EMBEDDING_MODEL_NAME,
        input=text,
    )
    embeddings = response.embeddings
    if not embeddings:
        return []
    return embeddings[0]
