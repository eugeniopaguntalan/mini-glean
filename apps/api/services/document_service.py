"""
Document Service
Business logic for document ingestion and management
"""

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import urlparse

from config import settings
from schemas import DocumentResponse
from models import Chunk
from repositories.document_repository import DocumentRepository
from repositories.chunk_repository import ChunkRepository
from services import parser, chunker, embedder
from services.exceptions import (
    DocumentNotFoundError,
    DocumentLimitExceededError,
)


async def ingest_pdf(
    file_content: bytes,
    filename: str,
    session: AsyncSession
) -> DocumentResponse:
    """
    Ingest a PDF document
    
    Args:
        file_content: PDF file bytes
        filename: Original filename
        session: Database session
        
    Returns:
        DocumentResponse with metadata
        
    Raises:
        DocumentLimitExceededError: If document limit reached
        PageLimitExceededError: If PDF has too many pages
        ParseError: If PDF parsing fails
        EmbeddingError: If embedding generation fails
    """
    # Check document limit first (fail fast)
    doc_repo = DocumentRepository(session)
    current_count = await doc_repo.count()
    
    if current_count >= settings.MAX_DOCUMENTS:
        raise DocumentLimitExceededError(
            f"Maximum document limit ({settings.MAX_DOCUMENTS}) reached"
        )
    
    # Parse PDF to extract text
    text = parser.parse_pdf(file_content)
    
    # Chunk the text
    chunks = chunker.chunk_text(
        text,
        chunk_size=settings.CHUNK_SIZE,
        overlap=settings.CHUNK_OVERLAP
    )
    
    # Generate embeddings
    embeddings = embedder.embed_chunks(chunks)
    
    # Create document record
    document = await doc_repo.create(
        filename=filename,
        doc_type='pdf',
        tags=[]
    )
    
    # Update chunk count
    document.chunk_count = len(chunks)
    await session.commit()
    await session.refresh(document)
    
    # Create chunk records
    chunk_repo = ChunkRepository(session)
    chunk_models = [
        Chunk(
            document_id=document.id,
            content=chunk_text,
            embedding=embedding,
            chunk_index=idx
        )
        for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings))
    ]
    await chunk_repo.add_chunks(chunk_models)
    
    return DocumentResponse.model_validate(document)


async def ingest_url(url: str, session: AsyncSession) -> DocumentResponse:
    """
    Ingest a web page from URL
    
    Args:
        url: URL to fetch and ingest
        session: Database session
        
    Returns:
        DocumentResponse with metadata
        
    Raises:
        DocumentLimitExceededError: If document limit reached
        ParseError: If URL parsing fails
        EmbeddingError: If embedding generation fails
    """
    # Check document limit first (fail fast)
    doc_repo = DocumentRepository(session)
    current_count = await doc_repo.count()
    
    if current_count >= settings.MAX_DOCUMENTS:
        raise DocumentLimitExceededError(
            f"Maximum document limit ({settings.MAX_DOCUMENTS}) reached"
        )
    
    # Parse URL to extract text and title
    text, page_title = parser.parse_url(url)
    
    # Use page title as filename, fallback to hostname
    if page_title and page_title != url:
        filename = page_title[:200]  # Limit filename length
    else:
        parsed = urlparse(url)
        filename = parsed.netloc or url
    
    # Chunk the text
    chunks = chunker.chunk_text(
        text,
        chunk_size=settings.CHUNK_SIZE,
        overlap=settings.CHUNK_OVERLAP
    )
    
    # Generate embeddings
    embeddings = embedder.embed_chunks(chunks)
    
    # Create document record
    document = await doc_repo.create(
        filename=filename,
        doc_type='url',
        tags=[]
    )
    
    # Update chunk count
    document.chunk_count = len(chunks)
    await session.commit()
    await session.refresh(document)
    
    # Create chunk records
    chunk_repo = ChunkRepository(session)
    chunk_models = [
        Chunk(
            document_id=document.id,
            content=chunk_text,
            embedding=embedding,
            chunk_index=idx
        )
        for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings))
    ]
    await chunk_repo.add_chunks(chunk_models)
    
    return DocumentResponse.model_validate(document)


async def ingest_note(
    content: str,
    tags: List[str],
    session: AsyncSession
) -> DocumentResponse:
    """
    Ingest a plain text note
    
    Args:
        content: Note content
        tags: Optional tags for the note
        session: Database session
        
    Returns:
        DocumentResponse with metadata
        
    Raises:
        DocumentLimitExceededError: If document limit reached
        ParseError: If note content is empty
        EmbeddingError: If embedding generation fails
    """
    # Check document limit first (fail fast)
    doc_repo = DocumentRepository(session)
    current_count = await doc_repo.count()
    
    if current_count >= settings.MAX_DOCUMENTS:
        raise DocumentLimitExceededError(
            f"Maximum document limit ({settings.MAX_DOCUMENTS}) reached"
        )
    
    # Parse note (validates not empty)
    text = parser.parse_note(content)
    
    # Generate filename from first 50 chars or use default
    if len(text) > 50:
        filename = text[:50] + "..."
    else:
        filename = text if text else "Untitled Note"
    
    # Chunk the text
    chunks = chunker.chunk_text(
        text,
        chunk_size=settings.CHUNK_SIZE,
        overlap=settings.CHUNK_OVERLAP
    )
    
    # Generate embeddings
    embeddings = embedder.embed_chunks(chunks)
    
    # Create document record
    document = await doc_repo.create(
        filename=filename,
        doc_type='note',
        tags=tags or []
    )
    
    # Update chunk count
    document.chunk_count = len(chunks)
    await session.commit()
    await session.refresh(document)
    
    # Create chunk records
    chunk_repo = ChunkRepository(session)
    chunk_models = [
        Chunk(
            document_id=document.id,
            content=chunk_text,
            embedding=embedding,
            chunk_index=idx
        )
        for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings))
    ]
    await chunk_repo.add_chunks(chunk_models)
    
    return DocumentResponse.model_validate(document)


async def list_documents(session: AsyncSession) -> List[DocumentResponse]:
    """
    List all documents
    
    Args:
        session: Database session
        
    Returns:
        List of DocumentResponse ordered by created_at descending
    """
    doc_repo = DocumentRepository(session)
    documents = await doc_repo.list_all()
    
    return [DocumentResponse.model_validate(doc) for doc in documents]


async def delete_document(doc_id: str, session: AsyncSession) -> None:
    """
    Delete a document and all its chunks
    
    Args:
        doc_id: Document ID
        session: Database session
        
    Raises:
        DocumentNotFoundError: If document doesn't exist
    """
    doc_repo = DocumentRepository(session)
    
    # Check if document exists
    document = await doc_repo.get_by_id(doc_id)
    if not document:
        raise DocumentNotFoundError(f"Document {doc_id} not found")
    
    # Delete document (CASCADE will remove chunks)
    await doc_repo.delete(doc_id)
