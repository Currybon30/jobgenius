import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.helpers.embedding_helper import embed_text


@pytest.mark.asyncio
async def test_embed_text_returns_first_vector():
    mock_embedding_model = MagicMock()
    mock_embedding_model.aembed_query = AsyncMock(
        return_value=[0.1, 0.2, 0.3]
    )

    with patch("app.helpers.embedding_helper.OllamaEmbeddings", return_value=mock_embedding_model):
        result = await embed_text("hello world")

    assert result == [0.1, 0.2, 0.3]
    

@pytest.mark.asyncio
async def test_embed_text_empty_embeddings():
    mock_embedding_model = MagicMock()
    mock_embedding_model.aembed_query = AsyncMock(return_value=[])

    with patch("app.helpers.embedding_helper.OllamaEmbeddings", return_value=mock_embedding_model):
        result = await embed_text("anything")

    assert result == []


@pytest.mark.asyncio
async def test_embed_text_none_embeddings():
    mock_embedding_model = MagicMock()
    mock_embedding_model.aembed_query = AsyncMock(return_value=None)

    with patch("app.helpers.embedding_helper.OllamaEmbeddings", return_value=mock_embedding_model):
        result = await embed_text("anything")

    assert result == None
