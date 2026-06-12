"""
Unit Tests for Retriever Service
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from services.retriever import retrieve


@pytest.mark.asyncio
async def test_retrieve_returns_relevant_chunks():
    """Should return relevant chunks above similarity threshold"""
    # Mock embedder
    mock_embedding = [0.1] * 1536
    
    # Mock repository results with high similarity (low distance)
    mock_results = [
        {
            "id": "chunk1",
            "content": "Test content 1",
            "chunk_index": 0,
            "distance": 0.2,  # similarity = 0.8
            "document_id": "doc1",
            "filename": "test1.pdf",
            "type": "pdf"
        },
        {
            "id": "chunk2",
            "content": "Test content 2",
            "chunk_index": 1,
            "distance": 0.3,  # similarity = 0.7
            "document_id": "doc2",
            "filename": "test2.pdf",
            "type": "pdf"
        }
    ]
    
    mock_repo = MagicMock()
    mock_repo.search_similar = AsyncMock(return_value=mock_results)
    
    with patch('services.retriever.embed_query', return_value=mock_embedding):
        chunks = await retrieve("test question", mock_repo, top_k=5)
    
    assert len(chunks) == 2
    assert chunks[0].chunk_id == "chunk1"
    assert chunks[0].similarity == 0.8
    assert chunks[1].chunk_id == "chunk2"
    assert chunks[1].similarity == 0.7


@pytest.mark.asyncio
async def test_retrieve_returns_empty_when_no_matches():
    """Should return empty list when repository returns no results"""
    mock_embedding = [0.1] * 1536
    mock_repo = MagicMock()
    mock_repo.search_similar = AsyncMock(return_value=[])
    
    with patch('services.retriever.embed_query', return_value=mock_embedding):
        chunks = await retrieve("test question", mock_repo, top_k=5)
    
    assert len(chunks) == 0


@pytest.mark.asyncio
async def test_retrieve_filters_low_similarity():
    """Should filter out chunks below similarity threshold"""
    mock_embedding = [0.1] * 1536
    
    # Mock results with low similarity (high distance)
    mock_results = [
        {
            "id": "chunk1",
            "content": "Irrelevant content",
            "chunk_index": 0,
            "distance": 0.75,  # similarity = 0.25 (below 0.3 threshold)
            "document_id": "doc1",
            "filename": "test1.pdf",
            "type": "pdf"
        }
    ]
    
    mock_repo = MagicMock()
    mock_repo.search_similar = AsyncMock(return_value=mock_results)
    
    with patch('services.retriever.embed_query', return_value=mock_embedding):
        chunks = await retrieve("test question", mock_repo, top_k=5)
    
    # Should filter out the low-similarity chunk
    assert len(chunks) == 0


@pytest.mark.asyncio
async def test_retrieve_respects_top_k():
    """Should pass top_k parameter to repository"""
    mock_embedding = [0.1] * 1536
    
    # Mock 3 results
    mock_results = [
        {
            "id": f"chunk{i}",
            "content": f"Content {i}",
            "chunk_index": i,
            "distance": 0.2,
            "document_id": f"doc{i}",
            "filename": f"test{i}.pdf",
            "type": "pdf"
        }
        for i in range(3)
    ]
    
    mock_repo = MagicMock()
    mock_repo.search_similar = AsyncMock(return_value=mock_results)
    
    with patch('services.retriever.embed_query', return_value=mock_embedding):
        chunks = await retrieve("test question", mock_repo, top_k=3)
    
    # Verify repository was called with top_k=3
    mock_repo.search_similar.assert_called_once_with(mock_embedding, 3)
    assert len(chunks) == 3
