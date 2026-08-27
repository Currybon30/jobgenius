import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from app.helpers.embedding_helper import embed_text


@pytest.mark.asyncio
async def test_embed_text_returns_first_vector():
    mock_client = MagicMock()
    mock_client.embed = AsyncMock(
        return_value=SimpleNamespace(embeddings=[[0.1, 0.2, 0.3]])
    )

    with (
        patch("app.helpers.embedding_helper.get_ollama_client", return_value=mock_client),
        patch("app.helpers.embedding_helper.settings") as settings,
    ):
        settings.EMBEDDING_MODEL_NAME = "nomic-embed-text-v2-moe:latest"
        result = await embed_text("hello world")

    assert result == [0.1, 0.2, 0.3]
    mock_client.embed.assert_awaited_once_with(
        model="nomic-embed-text-v2-moe:latest",
        input="hello world",
    )


@pytest.mark.asyncio
async def test_embed_text_empty_embeddings():
    mock_client = MagicMock()
    mock_client.embed = AsyncMock(return_value=SimpleNamespace(embeddings=[]))

    with patch(
        "app.helpers.embedding_helper.get_ollama_client",
        return_value=mock_client,
    ):
        result = await embed_text("anything")

    assert result == []


@pytest.mark.asyncio
async def test_embed_text_none_embeddings():
    mock_client = MagicMock()
    mock_client.embed = AsyncMock(return_value=SimpleNamespace(embeddings=None))

    with patch(
        "app.helpers.embedding_helper.get_ollama_client",
        return_value=mock_client,
    ):
        result = await embed_text("anything")

    assert result == []
