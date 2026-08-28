import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from app.helpers.embedding_helper import embed_text
from app.core.ollama_config import get_ollama_embedding_model


@pytest.mark.asyncio
async def test_embed_text_returns_first_vector():
    mock_embedding_model = MagicMock()
    mock_embedding_model.aembed_query = AsyncMock(
        return_value=SimpleNamespace(embeddings=[0.1, 0.2, 0.3])
    )

    with (
        patch("app.helpers.embedding_helper.get_ollama_embedding_model", return_value=mock_embedding_model),
    ):
        result = await embed_text("hello world")

    assert result == [0.1, 0.2, 0.3]
    
    


@pytest.mark.asyncio
async def test_embed_text_empty_embeddings():
    mock_embedding_model = MagicMock()
    mock_embedding_model.aembed_query = AsyncMock(return_value=SimpleNamespace(embeddings=[]))

    with patch(
        "app.helpers.embedding_helper.get_ollama_embedding_model",
        return_value=mock_embedding_model,
    ):
        result = await embed_text("anything")

    assert result == []


@pytest.mark.asyncio
async def test_embed_text_none_embeddings():
    mock_embedding_model = MagicMock()
    mock_embedding_model.aembed_query = AsyncMock(return_value=SimpleNamespace(embeddings=None))

    with patch(
        "app.helpers.embedding_helper.get_ollama_embedding_model",
        return_value=mock_embedding_model,
    ):
        result = await embed_text("anything")

    assert result == []
