"""
Unit Tests for the add_note Tool
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from langchain_core.tools import ToolException

from tools.add_note import add_note


@pytest.mark.asyncio
async def test_returns_confirmation():
    """A saved note returns a confirmation with ID and chunk count"""
    session = MagicMock()
    document = MagicMock()
    document.id = "note123"
    document.chunk_count = 2

    with patch(
        "tools.add_note.document_service.ingest_note",
        new_callable=AsyncMock,
        return_value=document,
    ):
        result = await add_note("remember this", ["tag"], session)

    assert result == "Note saved with ID 'note123' and 2 chunk(s)."


@pytest.mark.asyncio
async def test_raises_tool_exception_on_failure():
    """A failure during ingestion surfaces as a ToolException"""
    session = MagicMock()

    with patch(
        "tools.add_note.document_service.ingest_note",
        new_callable=AsyncMock,
        side_effect=RuntimeError("boom"),
    ):
        with pytest.raises(ToolException):
            await add_note("remember this", [], session)
