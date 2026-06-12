"""
Chat Router
Endpoint for question answering via RAG
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas import ChatRequest, ChatResponse
from services import chat_service
from services.exceptions import EmbeddingError, LLMError
from repositories.chunk_repository import ChunkRepository


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
) -> ChatResponse:
    """
    Answer a question using RAG
    
    Retrieves relevant chunks from the knowledge base and generates
    a grounded answer with source citations.
    
    Returns:
        ChatResponse with answer and sources
        
    Raises:
        HTTPException 502: If embedding or LLM service fails
        HTTPException 422: If validation fails
    """
    try:
        # Create repository
        chunk_repo = ChunkRepository(db)
        
        # Ask the question
        response = await chat_service.ask(request.question, chunk_repo)
        
        return response
        
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
