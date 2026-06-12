"""
Chat Router
Endpoint for question answering via RAG
"""

import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.tools import ToolException
from database import get_session
from schemas import ChatRequest, ChatResponse
from services import chat_service
from services.chat_service import SourcesEvent, TokenEvent
from services.exceptions import EmbeddingError, LLMError


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    session: AsyncSession = Depends(get_session)
) -> ChatResponse:
    """
    Answer a question using the agent

    The agent decides which tools to use (search, summarize, compare,
    add note) and produces a grounded answer with source citations.
    Conversation history is tracked per session_id.

    Returns:
        ChatResponse with answer, sources, and session_id

    Raises:
        HTTPException 500: If a tool fails to execute
        HTTPException 502: If embedding or LLM service fails
        HTTPException 422: If validation fails
    """
    try:
        response = await chat_service.ask(
            request.question,
            request.session_id,
            session,
        )
        return response

    except ToolException:
        raise HTTPException(
            status_code=500,
            detail="Tool execution failed"
        )
    except EmbeddingError:
        raise HTTPException(
            status_code=502,
            detail="Embedding service unavailable"
        )
    except LLMError:
        raise HTTPException(
            status_code=502,
            detail="LLM service unavailable"
        )


# Sentinel the client uses to recognise the final source-citation event
_SOURCES_PREFIX = "[SOURCES]"


def _format_sse(payload: str) -> str:
    """
    Encode a payload as a single SSE event

    Splits the payload across multiple `data:` lines so that embedded newlines
    survive transport (the client rejoins them with `\\n`).
    """
    lines = payload.split("\n")
    body = "".join(f"data: {line}\n" for line in lines)
    return f"{body}\n"


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    session: AsyncSession = Depends(get_session),
) -> StreamingResponse:
    """
    Stream an answer to a question as Server-Sent Events

    Emits answer tokens as `data: <token>` events in real time, then a single
    `data: [SOURCES]<json>` event carrying the source citations, and finally a
    `data: [DONE]` marker.

    Returns:
        StreamingResponse with media type text/event-stream
    """
    async def event_gen():
        try:
            async for event in chat_service.stream(
                request.question,
                request.session_id,
                session,
            ):
                if isinstance(event, TokenEvent):
                    yield _format_sse(event.text)
                elif isinstance(event, SourcesEvent):
                    sources = [source.model_dump() for source in event.sources]
                    yield _format_sse(_SOURCES_PREFIX + json.dumps(sources))
        except (ToolException, EmbeddingError, LLMError):
            # Surface a terminal marker so the client closes the stream cleanly.
            pass
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
