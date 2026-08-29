from app.core.config import settings
from langchain_ollama import OllamaEmbeddings


async def embed_text(text: str):
    ollama_embedding_model = OllamaEmbeddings(
        model=settings.EMBEDDING_MODEL,
        base_url=settings.OLLAMA_HOST,
    )
    response = await ollama_embedding_model.aembed_query(text)
    return response
