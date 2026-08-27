from ollama import AsyncClient
import asyncio
from app.core.config import settings

ollama_client = AsyncClient("http://localhost:11434")

async def embed_text(text: str) -> list[float]:
    response = await ollama_client.embed(
        model=settings.EMBEDDING_MODEL_NAME,
        input=text,
    )
    embeddings = response.embeddings
    if not embeddings:
        return []
    return embeddings

async def test_main():
    text = "I am a software engineer with 5 years of experience in developing web applications using React, Node.js, and MongoDB. I have a strong understanding of the software development lifecycle and am able to work independently and as part of a team."
    embedding = await embed_text(text)
    print(embedding)

asyncio.run(test_main())