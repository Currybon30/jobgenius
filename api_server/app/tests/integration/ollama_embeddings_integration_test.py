import pytest

from app.helpers.embedding_helper import embed_text

SAMPLE_TEXT = (
    "Software engineer with experience in Python, FastAPI, and MongoDB."
)


@pytest.mark.asyncio
async def test_embed_text_returns_vector():
    embedding = await embed_text(SAMPLE_TEXT)
    print(embedding)
    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert all(isinstance(value, float) for value in embedding)


@pytest.mark.asyncio
async def test_embed_text_same_input_same_dimension():
    first = await embed_text(SAMPLE_TEXT)
    second = await embed_text(SAMPLE_TEXT)

    assert len(first) == len(second)
    assert first == second
