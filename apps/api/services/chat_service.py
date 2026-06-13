"""
Chat Service
Routes user questions through the LangChain agent and builds the response
with source citations.
"""

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import AsyncGenerator, List, Union
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.document_repository import DocumentRepository
from repositories.chunk_repository import ChunkRepository
from services import agent
from services import agent_mock
from config import settings
from schemas import ChatResponse, SourceCitation


# Matches [source: doc_id] and [sources: id_a, id_b]
_SOURCE_PATTERN = re.compile(
    r"\[sources?:\s*([a-f0-9][a-f0-9\-,\s]*)\]",
    re.IGNORECASE,
)


@dataclass
class TokenEvent:
    """A single streamed answer token."""
    text: str


@dataclass
class SourcesEvent:
    """The final source citations, emitted once streaming completes."""
    sources: List[SourceCitation] = field(default_factory=list)


# A streamed chat event is either an answer token or the trailing sources.
StreamEvent = Union[TokenEvent, SourcesEvent]


async def ask(
    question: str,
    session_id: str,
    session: AsyncSession,
) -> ChatResponse:
    """
    Answer a question by invoking the agent and attaching source citations

    Args:
        question: The user's question
        session_id: The conversation session identifier
        session: The active database session

    Returns:
        ChatResponse with the agent's answer, sources, and session_id
    """
    # Route through the agent (mock or real based on config)
    if settings.USE_MOCK_LLM:
        agent_response = await agent_mock.invoke(question, session_id, session)
    else:
        agent_response = await agent.invoke(question, session_id, session)

    # Parse cited source document IDs from the response content
    doc_ids = _parse_source_ids(agent_response.content)

    # Build source citations by looking up document metadata
    sources = await _build_sources(doc_ids, session)

    return ChatResponse(
        id=str(uuid.uuid4()),
        content=agent_response.content,
        sources=sources,
        created_at=datetime.now(UTC).isoformat(),
        session_id=session_id,
    )


async def stream(
    question: str,
    session_id: str,
    session: AsyncSession,
) -> AsyncGenerator[StreamEvent, None]:
    """
    Stream an answer token by token, then emit source citations

    Yields a :class:`TokenEvent` for every answer token as it is generated.
    Once the answer is complete, the accumulated content is parsed for cited
    document IDs and a single :class:`SourcesEvent` is emitted.

    Args:
        question: The user's question
        session_id: The conversation session identifier
        session: The active database session

    Yields:
        TokenEvent for each token, then a final SourcesEvent
    """
    collected: List[str] = []
    
    # Use mock streaming in demo mode
    if settings.USE_MOCK_LLM:
        async for token in agent_mock.stream(question, session_id, session):
            collected.append(token)
            yield TokenEvent(text=token)
    else:
        async for token in agent.astream(question, session_id, session):
            collected.append(token)
            yield TokenEvent(text=token)

    content = "".join(collected)
    doc_ids = _parse_source_ids(content)
    sources = await _build_sources(doc_ids, session)
    yield SourcesEvent(sources=sources)


def _parse_source_ids(content: str) -> List[str]:
    """
    Extract and deduplicate source document IDs from response content

    Args:
        content: The agent response text

    Returns:
        Deduplicated list of document IDs in order of first appearance
    """
    doc_ids: List[str] = []
    for match in _SOURCE_PATTERN.finditer(content):
        raw = match.group(1)
        for part in raw.split(","):
            doc_id = part.strip()
            if doc_id and doc_id not in doc_ids:
                doc_ids.append(doc_id)
    return doc_ids


async def _build_sources(
    doc_ids: List[str],
    session: AsyncSession,
) -> List[SourceCitation]:
    """
    Build source citations from cited document IDs

    Args:
        doc_ids: The cited document IDs
        session: The active database session

    Returns:
        List of SourceCitation objects (skips IDs that don't resolve)
    """
    doc_repo = DocumentRepository(session)
    chunk_repo = ChunkRepository(session)

    sources: List[SourceCitation] = []
    for doc_id in doc_ids:
        document = await doc_repo.get_by_id(doc_id)
        if document is None:
            continue

        # Use the first chunk as a preview excerpt
        excerpt = ""
        chunks = await chunk_repo.get_by_document_id(doc_id)
        if chunks:
            excerpt = chunks[0].content[:100]
            if len(chunks[0].content) > 100:
                excerpt += "..."

        sources.append(SourceCitation(
            doc_id=doc_id,
            filename=document.filename,
            excerpt=excerpt,
        ))

    return sources
