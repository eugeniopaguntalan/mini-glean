"""
Unit Tests for the summarize_document Tool
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from tools.summarize_document import summarize_document


def _chunk(content):
    chunk = MagicMock()
    chunk.content = content
    return chunk


@pytest.mark.asyncio
async def test_returns_summary_with_source():
    """A successful summary includes the document source citation"""
    repo = MagicMock()
    repo.get_by_document_id = AsyncMock(return_value=[
        _chunk("part one"),
        _chunk("part two"),
    ])

    with patch("tools.summarize_document.llm.summarize", return_value="A short summary."):
        result = await summarize_document("doc1", repo)

    assert "[source: doc1]" in result
    assert "A short summary." in result


@pytest.mark.asyncio
async def test_returns_not_found_for_missing_doc():
    """An unknown document yields the not-found message"""
    repo = MagicMock()
    repo.get_by_document_id = AsyncMock(return_value=[])

    result = await summarize_document("missing", repo)

    assert result == "No document found with ID 'missing'"


@pytest.mark.asyncio
async def test_calls_llm_with_concatenated_content():
    """The LLM is called with all chunk content concatenated"""
    repo = MagicMock()
    repo.get_by_document_id = AsyncMock(return_value=[
        _chunk("alpha"),
        _chunk("beta"),
    ])

    with patch("tools.summarize_document.llm.summarize", return_value="ok") as mock_summarize:
        await summarize_document("doc1", repo)

    mock_summarize.assert_called_once_with("alpha\n\nbeta")
