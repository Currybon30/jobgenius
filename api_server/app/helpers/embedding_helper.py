from app.core.ollama_config import get_ollama_embedding_model


async def embed_text(text: str):
    ollama_embedding_model = get_ollama_embedding_model()
    response = await ollama_embedding_model.aembed_query(text)
    return response
