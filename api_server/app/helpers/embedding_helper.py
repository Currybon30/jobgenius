from app.core.ollama_config import get_ollama_client
from app.core.config import settings

ollama_client = get_ollama_client()

async def embed_text(text: str) -> list[float]:
    response = await ollama_client.embed(
        model=settings.EMBEDDING_MODEL_NAME,
        input=text
    )
    return response.embeddings