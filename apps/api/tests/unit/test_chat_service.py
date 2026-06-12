"""
Unit Tests for the Chat Service (agent-based)
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from services.chat_service import ask, _parse_source_ids
from services.agent import AgentResponse


@pytest.mark.asyncio
async def test_routes_through_agent():
    """The chat service delegates to the agent, not direct retrieval"""
    session = MagicMock()
    agent_response = AgentResponse(content="An answer with no sources.")

    with patch(
        "services.chat_service.agent.invoke",
        new_callable=AsyncMock,
        return_value=agent_response,
    ) as mock_invoke:
        response = await ask("a question", "sess-1", session)

    mock_invoke.assert_awaited_once_with("a question", "sess-1", session)
    assert response.content == "An answer with no sources."
    assert response.sources == []


@pytest.mark.asyncio
async def test_parses_source_doc_ids_and_builds_citations():
    """Cited doc IDs are parsed and resolved into source citations"""
    session = MagicMock()
    agent_response = AgentResponse(content="Here it is [source: abc].")

    document = MagicMock()
    document.filename = "abc.pdf"

    chunk = MagicMock()
    chunk.content = "x" * 150  # long enough to be truncated

    doc_repo = MagicMock()
    doc_repo.get_by_id = AsyncMock(return_value=document)
    chunk_repo = MagicMock()
    chunk_repo.get_by_document_id = AsyncMock(return_value=[chunk])

    with patch("services.chat_service.agent.invoke", new_callable=AsyncMock, return_value=agent_response), \
         patch("services.chat_service.DocumentRepository", return_value=doc_repo), \
         patch("services.chat_service.ChunkRepository", return_value=chunk_repo):
        response = await ask("question", "sess-1", session)

    assert len(response.sources) == 1
    assert response.sources[0].doc_id == "abc"
    assert response.sources[0].filename == "abc.pdf"
    assert response.sources[0].excerpt == "x" * 100 + "..."


@pytest.mark.asyncio
async def test_skips_unresolved_doc_ids():
    """Cited IDs that do not resolve to a document are skipped"""
    session = MagicMock()
    agent_response = AgentResponse(content="Cited [source: ghost].")

    doc_repo = MagicMock()
    doc_repo.get_by_id = AsyncMock(return_value=None)
    chunk_repo = MagicMock()
    chunk_repo.get_by_document_id = AsyncMock(return_value=[])

    with patch("services.chat_service.agent.invoke", new_callable=AsyncMock, return_value=agent_response), \
         patch("services.chat_service.DocumentRepository", return_value=doc_repo), \
         patch("services.chat_service.ChunkRepository", return_value=chunk_repo):
        response = await ask("question", "sess-1", session)

    assert response.sources == []


@pytest.mark.asyncio
async def test_returns_session_id():
    """The response echoes the session_id back to the caller"""
    session = MagicMock()
    agent_response = AgentResponse(content="No sources here.")

    with patch("services.chat_service.agent.invoke", new_callable=AsyncMock, return_value=agent_response):
        response = await ask("question", "my-session", session)

    assert response.session_id == "my-session"
    assert response.id is not None
    assert response.created_at is not None


@pytest.mark.asyncio
async def test_propagates_agent_error():
    """Errors from the agent propagate for the router to handle"""
    session = MagicMock()

    with patch(
        "services.chat_service.agent.invoke",
        new_callable=AsyncMock,
        side_effect=RuntimeError("agent boom"),
    ):
        with pytest.raises(RuntimeError):
            await ask("question", "sess-1", session)


def test_parse_source_ids_dedupes():
    """Both [source:] and [sources:] formats are parsed and deduped"""
    content = "[source: abc] and [sources: def, abc]"
    assert _parse_source_ids(content) == ["abc", "def"]
