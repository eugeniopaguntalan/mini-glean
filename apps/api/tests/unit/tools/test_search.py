"""
Unit Tests for the search_knowledge_base Tool
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from langchain_core.tools import ToolException

from tools.search_knowledge_base import search_knowledge_base


def _result(document_id, filename, content, distance):
    return {
        "id": "chunk",
        "content": content,
        "chunk_index": 0,
        "distance": distance,
        "document_id": document_id,
        "filename": filename,
        "type": "pdf",
    }


@pytest.mark.asyncio
async def test_returns_formatted_chunks():
    """Relevant chunks are formatted with [source: ...] citations"""
    repo = MagicMock()
    repo.search_similar = AsyncMock(return_value=[
        _result("doc1", "a.pdf", "first chunk", 0.1),
        _result("doc2", "b.pdf", "second chunk", 0.2),
    ])

    with patch("tools.search_knowledge_base.embedder.embed_query", return_value=[0.0] * 1536):
        result = await search_knowledge_base("query", 5, repo)

    assert "[source: doc1 | a.pdf]" in result
    assert "first chunk" in result
    assert "[source: doc2 | b.pdf]" in result
    assert "second chunk" in result
    assert "\n\n---\n\n" in result


@pytest.mark.asyncio
async def test_returns_not_found_when_empty():
    """No results yields the not-found message"""
    repo = MagicMock()
    repo.search_similar = AsyncMock(return_value=[])

    with patch("tools.search_knowledge_base.embedder.embed_query", return_value=[0.0] * 1536):
        result = await search_knowledge_base("query", 5, repo)

    assert result == "No relevant documents found"


@pytest.mark.asyncio
async def test_filters_below_threshold():
    """Chunks with similarity at or below 0.3 are excluded"""
    repo = MagicMock()
    repo.search_similar = AsyncMock(return_value=[
        # similarity = 1 - 0.9 = 0.1 → below threshold, excluded
        _result("doc1", "a.pdf", "low relevance", 0.9),
        # similarity = 1 - 0.2 = 0.8 → above threshold, included
        _result("doc2", "b.pdf", "high relevance", 0.2),
    ])

    with patch("tools.search_knowledge_base.embedder.embed_query", return_value=[0.0] * 1536):
        result = await search_knowledge_base("query", 5, repo)

    assert "low relevance" not in result
    assert "high relevance" in result


@pytest.mark.asyncio
async def test_raises_tool_exception_on_error():
    """A repository failure surfaces as a ToolException"""
    repo = MagicMock()
    repo.search_similar = AsyncMock(side_effect=RuntimeError("db down"))

    with patch("tools.search_knowledge_base.embedder.embed_query", return_value=[0.0] * 1536):
        with pytest.raises(ToolException):
            await search_knowledge_base("query", 5, repo)
