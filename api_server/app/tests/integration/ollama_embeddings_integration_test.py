import pytest

from app.core.ollama_config import close_ollama, init_ollama
from app.helpers.embedding_helper import embed_text

SAMPLE_TEXT = (
    "Software engineer with experience in Python, FastAPI, and MongoDB."
)


@pytest.fixture
async def ollama():
    await init_ollama()
    yield
    await close_ollama()


@pytest.mark.asyncio
async def test_embed_text_returns_vector(ollama):
    embedding = await embed_text(SAMPLE_TEXT)
    print(embedding)
    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert all(isinstance(value, float) for value in embedding)


@pytest.mark.asyncio
async def test_embed_text_same_input_same_dimension(ollama):
    first = await embed_text(SAMPLE_TEXT)
    second = await embed_text(SAMPLE_TEXT)

    assert len(first) == len(second)
    assert first == second
