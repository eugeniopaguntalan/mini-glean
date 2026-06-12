"""
Documents Router
API endpoints for document ingestion and management
"""

from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from schemas import (
    DocumentResponse,
    UrlIngestRequest,
    NoteIngestRequest,
)
from services import document_service
from services.exceptions import (
    DocumentNotFoundError,
    DocumentLimitExceededError,
    InvalidFileTypeError,
    FileTooLargeError,
    PageLimitExceededError,
    ParseError,
    EmbeddingError,
)


router = APIRouter(prefix="/documents", tags=["documents"])


# Maximum file size: 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes


@router.post("/upload/pdf", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session)
) -> DocumentResponse:
    """
    Upload and ingest a PDF document
    
    - Validates file type and size
    - Extracts text, chunks, and embeds content
    - Stores in database
    """
    # Validate content type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF files accepted"
        )
    
    # Read file content
    content = await file.read()
    
    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds 10MB limit"
        )
    
    try:
        result = await document_service.ingest_pdf(
            file_content=content,
            filename=file.filename or "upload.pdf",
            session=session
        )
        return result
        
    except DocumentLimitExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except PageLimitExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="PDF exceeds 20 page limit"
        )
    except ParseError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Failed to parse document content"
        )
    except EmbeddingError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Embedding service unavailable"
        )


@router.post("/url", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def ingest_url(
    request: UrlIngestRequest,
    session: AsyncSession = Depends(get_session)
) -> DocumentResponse:
    """
    Ingest a web page from URL
    
    - Fetches and extracts text from HTML
    - Chunks and embeds content
    - Stores in database
    """
    try:
        result = await document_service.ingest_url(
            url=str(request.url),
            session=session
        )
        return result
        
    except DocumentLimitExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ParseError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Failed to parse document content"
        )
    except EmbeddingError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Embedding service unavailable"
        )


@router.post("/note", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    request: NoteIngestRequest,
    session: AsyncSession = Depends(get_session)
) -> DocumentResponse:
    """
    Create a plain text note
    
    - Chunks and embeds content
    - Stores in database with optional tags
    """
    try:
        result = await document_service.ingest_note(
            content=request.content,
            tags=request.tags or [],
            session=session
        )
        return result
        
    except DocumentLimitExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ParseError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Failed to parse document content"
        )
    except EmbeddingError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Embedding service unavailable"
        )


@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    session: AsyncSession = Depends(get_session)
) -> List[DocumentResponse]:
    """
    List all documents
    
    - Returns documents ordered by created_at descending
    """
    return await document_service.list_documents(session)


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: str,
    session: AsyncSession = Depends(get_session)
) -> None:
    """
    Delete a document and all its chunks
    
    - CASCADE automatically removes associated chunks
    """
    try:
        await document_service.delete_document(doc_id, session)
        
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
