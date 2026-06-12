"""
Unit Tests for Chat Service
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from services.chat_service import ask, _format_context, _extract_sources
from services.retriever import RetrievedChunk
from services.exceptions import EmbeddingError, LLMError


@pytest.mark.asyncio
async def test_ask_happy_path():
    """Should return answer with sources when chunks are found"""
    # Mock retrieved chunks
    mock_chunks = [
        RetrievedChunk(
            chunk_id="chunk1",
            content="This is relevant content about the topic.",
            document_id="doc1",
            filename="test.pdf",
            similarity=0.85
        ),
        RetrievedChunk(
            chunk_id="chunk2",
            content="More information about the same topic.",
            document_id="doc1",
            filename="test.pdf",
            similarity=0.75
        )
    ]
    
    mock_repo = MagicMock()
    
    with patch('services.chat_service.retriever.retrieve', new_callable=AsyncMock, return_value=mock_chunks):
        with patch('services.chat_service.llm.generate_answer', return_value="The answer is based on the provided context."):
            response = await ask("What is the topic?", mock_repo)
    
    assert response.content == "The answer is based on the provided context."
    assert len(response.sources) == 1  # Deduplicated by doc_id
    assert response.sources[0].doc_id == "doc1"
    assert response.sources[0].filename == "test.pdf"
    assert response.id is not None
    assert response.created_at is not None


@pytest.mark.asyncio
async def test_ask_no_context_found():
    """Should return refusal message when no chunks are found"""
    mock_repo = MagicMock()
    
    with patch('services.chat_service.retriever.retrieve', new_callable=AsyncMock, return_value=[]):
        response = await ask("What is quantum computing?", mock_repo)
    
    assert response.content == "I don't have that in my knowledge base."
    assert response.sources == []


@pytest.mark.asyncio
async def test_ask_sources_are_deduped():
    """Should deduplicate sources by document_id"""
    # Mock chunks from 2 documents
    mock_chunks = [
        RetrievedChunk("c1", "Content 1", "doc1", "file1.pdf", 0.9),
        RetrievedChunk("c2", "Content 2", "doc1", "file1.pdf", 0.8),
        RetrievedChunk("c3", "Content 3", "doc2", "file2.pdf", 0.7),
    ]
    
    mock_repo = MagicMock()
    
    with patch('services.chat_service.retriever.retrieve', new_callable=AsyncMock, return_value=mock_chunks):
        with patch('services.chat_service.llm.generate_answer', return_value="Answer"):
            response = await ask("Question", mock_repo)
    
    # Should have 2 sources (doc1 and doc2)
    assert len(response.sources) == 2


@pytest.mark.asyncio
async def test_ask_sources_include_excerpt():
    """Should include excerpt in source citations"""
    mock_chunks = [
        RetrievedChunk(
            "c1",
            "This is a very long piece of content that should be truncated to only show the first 100 characters as an excerpt for the user.",
            "doc1",
            "file1.pdf",
            0.9
        )
    ]
    
    mock_repo = MagicMock()
    
    with patch('services.chat_service.retriever.retrieve', new_callable=AsyncMock, return_value=mock_chunks):
        with patch('services.chat_service.llm.generate_answer', return_value="Answer"):
            response = await ask("Question", mock_repo)
    
    assert len(response.sources) == 1
    assert len(response.sources[0].excerpt) <= 103  # 100 chars + "..."
    assert response.sources[0].excerpt.endswith("...")


@pytest.mark.asyncio
async def test_ask_embedding_fails():
    """Should raise EmbeddingError when embedding fails"""
    mock_repo = MagicMock()
    
    with patch('services.chat_service.retriever.retrieve', new_callable=AsyncMock, side_effect=EmbeddingError("API Error")):
        with pytest.raises(EmbeddingError):
            await ask("Question", mock_repo)


@pytest.mark.asyncio
async def test_ask_llm_fails():
    """Should raise LLMError when LLM generation fails"""
    mock_chunks = [
        RetrievedChunk("c1", "Content", "doc1", "file1.pdf", 0.9)
    ]
    
    mock_repo = MagicMock()
    
    with patch('services.chat_service.retriever.retrieve', new_callable=AsyncMock, return_value=mock_chunks):
        with patch('services.chat_service.llm.generate_answer', side_effect=LLMError("API Error")):
            with pytest.raises(LLMError):
                await ask("Question", mock_repo)


def test_format_context():
    """Should format chunks with source citations"""
    chunks = [
        RetrievedChunk("c1", "First content", "doc1", "file1.pdf", 0.9),
        RetrievedChunk("c2", "Second content", "doc2", "file2.pdf", 0.8),
    ]
    
    context = _format_context(chunks)
    
    assert "[source: doc1 | file1.pdf]" in context
    assert "First content" in context
    assert "[source: doc2 | file2.pdf]" in context
    assert "Second content" in context
    assert "\n\n---\n\n" in context


def test_extract_sources():
    """Should extract and sort sources by similarity"""
    chunks = [
        RetrievedChunk("c1", "Content from doc2", "doc2", "file2.pdf", 0.7),
        RetrievedChunk("c2", "Content from doc1", "doc1", "file1.pdf", 0.9),
        RetrievedChunk("c3", "More from doc1", "doc1", "file1.pdf", 0.8),
    ]
    
    sources = _extract_sources(chunks)
    
    # Should have 2 sources (deduped)
    assert len(sources) == 2
    
    # Should be sorted by similarity (doc1 first with 0.9)
    assert sources[0].doc_id == "doc1"
    assert sources[1].doc_id == "doc2"
    
    # Should use highest similarity chunk for each doc
    assert "Content from doc1" in sources[0].excerpt
