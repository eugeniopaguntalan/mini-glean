"""
Unit Tests for the compare_documents Tool
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from tools.compare_documents import compare_documents


def _chunk(content):
    chunk = MagicMock()
    chunk.content = content
    return chunk


@pytest.mark.asyncio
async def test_returns_comparison_with_both_sources():
    """A successful comparison cites both document IDs"""
    repo = MagicMock()
    repo.get_by_document_id = AsyncMock(side_effect=[
        [_chunk("doc a content")],
        [_chunk("doc b content")],
    ])

    with patch("tools.compare_documents.llm.compare", return_value="They differ.") as mock_compare:
        result = await compare_documents("docA", "docB", repo)

    assert "[sources: docA, docB]" in result
    assert "They differ." in result
    mock_compare.assert_called_once_with("doc a content", "doc b content", "docA", "docB")


@pytest.mark.asyncio
async def test_returns_not_found_when_doc_a_missing():
    """A missing first document yields the not-found message"""
    repo = MagicMock()
    repo.get_by_document_id = AsyncMock(return_value=[])

    result = await compare_documents("docA", "docB", repo)

    assert result == "Document 'docA' not found"


@pytest.mark.asyncio
async def test_returns_not_found_when_doc_b_missing():
    """A missing second document yields the not-found message"""
    repo = MagicMock()
    repo.get_by_document_id = AsyncMock(side_effect=[
        [_chunk("doc a content")],
        [],
    ])

    result = await compare_documents("docA", "docB", repo)

    assert result == "Document 'docB' not found"
