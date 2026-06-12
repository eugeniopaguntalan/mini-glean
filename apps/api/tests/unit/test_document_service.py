"""
Unit tests for document service
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from services import document_service
from services.exceptions import DocumentNotFoundError, DocumentLimitExceededError
from models import Document


@pytest.mark.asyncio
@patch('services.document_service.parser')
@patch('services.document_service.chunker')
@patch('services.document_service.embedder')
async def test_ingest_pdf_happy_path(mock_embedder, mock_chunker, mock_parser):
    """PDF ingestion creates document with correct chunk count"""
    # Mock parser
    mock_parser.parse_pdf.return_value = "Extracted PDF text content"
    
    # Mock chunker
    mock_chunker.chunk_text.return_value = ["Chunk 1", "Chunk 2", "Chunk 3"]
    
    # Mock embedder
    mock_embedder.embed_chunks.return_value = [
        [0.1] * 1536,
        [0.2] * 1536,
        [0.3] * 1536
    ]
    
    # Mock database session and repositories
    mock_session = AsyncMock()
    
    # Mock document
    mock_doc = Document(
        id="doc-123",
        filename="test.pdf",
        type="pdf",
        tags=[],
        chunk_count=3,
        created_at=datetime.now()
    )
    
    # Mock repository methods
    with patch('services.document_service.DocumentRepository') as mock_doc_repo_class, \
         patch('services.document_service.ChunkRepository') as mock_chunk_repo_class:
        
        mock_doc_repo = Mock()
        mock_doc_repo.count = AsyncMock(return_value=5)
        mock_doc_repo.create = AsyncMock(return_value=mock_doc)
        mock_doc_repo_class.return_value = mock_doc_repo
        
        mock_chunk_repo = Mock()
        mock_chunk_repo.add_chunks = AsyncMock()
        mock_chunk_repo_class.return_value = mock_chunk_repo
        
        # Call service
        result = await document_service.ingest_pdf(
            file_content=b"fake pdf content",
            filename="test.pdf",
            session=mock_session
        )
        
        # Verify
        assert result.id == "doc-123"
        assert result.filename == "test.pdf"
        assert result.type == "pdf"
        assert result.chunk_count == 3
        
        mock_doc_repo.count.assert_called_once()
        mock_doc_repo.create.assert_called_once()
        mock_chunk_repo.add_chunks.assert_called_once()


@pytest.mark.asyncio
@patch('services.document_service.parser')
@patch('services.document_service.chunker')
@patch('services.document_service.embedder')
async def test_ingest_url_happy_path(mock_embedder, mock_chunker, mock_parser):
    """URL ingestion creates document with type='url'"""
    # Mock parser
    mock_parser.parse_url.return_value = ("Page content", "Page Title")
    
    # Mock chunker
    mock_chunker.chunk_text.return_value = ["Chunk 1"]
    
    # Mock embedder
    mock_embedder.embed_chunks.return_value = [[0.1] * 1536]
    
    # Mock database session
    mock_session = AsyncMock()
    
    # Mock document
    mock_doc = Document(
        id="doc-456",
        filename="Page Title",
        type="url",
        tags=[],
        chunk_count=1,
        created_at=datetime.now()
    )
    
    with patch('services.document_service.DocumentRepository') as mock_doc_repo_class, \
         patch('services.document_service.ChunkRepository') as mock_chunk_repo_class:
        
        mock_doc_repo = Mock()
        mock_doc_repo.count = AsyncMock(return_value=3)
        mock_doc_repo.create = AsyncMock(return_value=mock_doc)
        mock_doc_repo_class.return_value = mock_doc_repo
        
        mock_chunk_repo = Mock()
        mock_chunk_repo.add_chunks = AsyncMock()
        mock_chunk_repo_class.return_value = mock_chunk_repo
        
        result = await document_service.ingest_url(
            url="https://example.com",
            session=mock_session
        )
        
        assert result.type == "url"
        assert result.filename == "Page Title"


@pytest.mark.asyncio
@patch('services.document_service.parser')
@patch('services.document_service.chunker')
@patch('services.document_service.embedder')
async def test_ingest_note_happy_path(mock_embedder, mock_chunker, mock_parser):
    """Note ingestion creates document with type='note'"""
    # Mock parser
    mock_parser.parse_note.return_value = "Note content here"
    
    # Mock chunker
    mock_chunker.chunk_text.return_value = ["Note content here"]
    
    # Mock embedder
    mock_embedder.embed_chunks.return_value = [[0.1] * 1536]
    
    # Mock database session
    mock_session = AsyncMock()
    
    # Mock document
    mock_doc = Document(
        id="doc-789",
        filename="Note content here",
        type="note",
        tags=["python", "test"],
        chunk_count=1,
        created_at=datetime.now()
    )
    
    with patch('services.document_service.DocumentRepository') as mock_doc_repo_class, \
         patch('services.document_service.ChunkRepository') as mock_chunk_repo_class:
        
        mock_doc_repo = Mock()
        mock_doc_repo.count = AsyncMock(return_value=0)
        mock_doc_repo.create = AsyncMock(return_value=mock_doc)
        mock_doc_repo_class.return_value = mock_doc_repo
        
        mock_chunk_repo = Mock()
        mock_chunk_repo.add_chunks = AsyncMock()
        mock_chunk_repo_class.return_value = mock_chunk_repo
        
        result = await document_service.ingest_note(
            content="Note content here",
            tags=["python", "test"],
            session=mock_session
        )
        
        assert result.type == "note"
        assert "python" in result.tags


@pytest.mark.asyncio
async def test_ingest_pdf_document_limit_exceeded():
    """Exceeding document limit raises DocumentLimitExceededError"""
    mock_session = AsyncMock()
    
    with patch('services.document_service.DocumentRepository') as mock_doc_repo_class:
        mock_doc_repo = Mock()
        mock_doc_repo.count = AsyncMock(return_value=20)  # At limit
        mock_doc_repo_class.return_value = mock_doc_repo
        
        with pytest.raises(DocumentLimitExceededError, match="Maximum document limit"):
            await document_service.ingest_pdf(
                file_content=b"pdf content",
                filename="test.pdf",
                session=mock_session
            )


@pytest.mark.asyncio
async def test_list_documents():
    """list_documents returns all documents"""
    mock_session = AsyncMock()
    
    # Mock documents
    mock_docs = [
        Document(
            id="doc-1",
            filename="Doc 1",
            type="pdf",
            tags=[],
            chunk_count=5,
            created_at=datetime.now()
        ),
        Document(
            id="doc-2",
            filename="Doc 2",
            type="note",
            tags=["tag1"],
            chunk_count=2,
            created_at=datetime.now()
        )
    ]
    
    with patch('services.document_service.DocumentRepository') as mock_doc_repo_class:
        mock_doc_repo = Mock()
        mock_doc_repo.list_all = AsyncMock(return_value=mock_docs)
        mock_doc_repo_class.return_value = mock_doc_repo
        
        result = await document_service.list_documents(mock_session)
        
        assert len(result) == 2
        assert result[0].id == "doc-1"
        assert result[1].id == "doc-2"


@pytest.mark.asyncio
async def test_delete_document_exists():
    """Deleting existing document succeeds"""
    mock_session = AsyncMock()
    
    mock_doc = Document(
        id="doc-123",
        filename="Test",
        type="pdf",
        tags=[],
        chunk_count=1,
        created_at=datetime.now()
    )
    
    with patch('services.document_service.DocumentRepository') as mock_doc_repo_class:
        mock_doc_repo = Mock()
        mock_doc_repo.get_by_id = AsyncMock(return_value=mock_doc)
        mock_doc_repo.delete = AsyncMock(return_value=True)
        mock_doc_repo_class.return_value = mock_doc_repo
        
        await document_service.delete_document("doc-123", mock_session)
        
        mock_doc_repo.get_by_id.assert_called_once_with("doc-123")
        mock_doc_repo.delete.assert_called_once_with("doc-123")


@pytest.mark.asyncio
async def test_delete_document_not_found():
    """Deleting non-existent document raises DocumentNotFoundError"""
    mock_session = AsyncMock()
    
    with patch('services.document_service.DocumentRepository') as mock_doc_repo_class:
        mock_doc_repo = Mock()
        mock_doc_repo.get_by_id = AsyncMock(return_value=None)
        mock_doc_repo_class.return_value = mock_doc_repo
        
        with pytest.raises(DocumentNotFoundError, match="not found"):
            await document_service.delete_document("nonexistent", mock_session)
