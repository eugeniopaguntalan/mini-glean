"""
Unit tests for embedder service
"""

import httpx
import pytest
from unittest.mock import Mock, patch
from openai import RateLimitError as OpenAIRateLimitError
from services.embedder import embed_chunks, embed_query
from services.exceptions import EmbeddingError, RateLimitError


def _openai_rate_limit_error() -> OpenAIRateLimitError:
    """Build a real openai.RateLimitError (needs an httpx response)."""
    request = httpx.Request("POST", "https://api.openai.com/v1/embeddings")
    response = httpx.Response(429, request=request)
    return OpenAIRateLimitError("rate limited", response=response, body=None)


@patch('services.embedder.client')
def test_embed_chunks_valid(mock_client):
    """Valid chunks return list of embeddings"""
    # Mock OpenAI response
    mock_embedding1 = Mock()
    mock_embedding1.embedding = [0.1] * 1536
    
    mock_embedding2 = Mock()
    mock_embedding2.embedding = [0.2] * 1536
    
    mock_response = Mock()
    mock_response.data = [mock_embedding1, mock_embedding2]
    
    mock_client.embeddings.create.return_value = mock_response
    
    chunks = ["First chunk", "Second chunk"]
    embeddings = embed_chunks(chunks)
    
    assert len(embeddings) == 2
    assert len(embeddings[0]) == 1536
    assert len(embeddings[1]) == 1536
    assert embeddings[0] == [0.1] * 1536
    assert embeddings[1] == [0.2] * 1536


@patch('services.embedder.client')
def test_embed_chunks_batching(mock_client):
    """Large number of chunks are batched correctly"""
    # Mock OpenAI response for batches
    def create_mock_response(batch):
        mock_data = []
        for _ in batch:
            mock_emb = Mock()
            mock_emb.embedding = [0.5] * 1536
            mock_data.append(mock_emb)
        
        mock_response = Mock()
        mock_response.data = mock_data
        return mock_response
    
    mock_client.embeddings.create.side_effect = lambda model, input: create_mock_response(input)
    
    # Create 45 chunks (should batch as 20 + 20 + 5)
    chunks = [f"Chunk {i}" for i in range(45)]
    embeddings = embed_chunks(chunks)
    
    assert len(embeddings) == 45
    assert mock_client.embeddings.create.call_count == 3  # 3 batches


@patch('services.embedder.client')
def test_embed_chunks_empty_list(mock_client):
    """Empty list returns empty list"""
    embeddings = embed_chunks([])
    
    assert embeddings == []
    mock_client.embeddings.create.assert_not_called()


@patch('services.embedder.client')
def test_embed_chunks_api_failure(mock_client):
    """OpenAI API failure raises EmbeddingError"""
    mock_client.embeddings.create.side_effect = Exception("API error")
    
    chunks = ["Test chunk"]
    
    with pytest.raises(EmbeddingError, match="Failed to generate embeddings"):
        embed_chunks(chunks)


@patch('services.embedder.client')
def test_embed_query_valid(mock_client):
    """Valid query returns single embedding"""
    mock_embedding = Mock()
    mock_embedding.embedding = [0.3] * 1536
    
    mock_response = Mock()
    mock_response.data = [mock_embedding]
    
    mock_client.embeddings.create.return_value = mock_response
    
    query = "Test query"
    embedding = embed_query(query)
    
    assert len(embedding) == 1536
    assert embedding == [0.3] * 1536


@patch('services.embedder.client')
def test_embed_query_api_failure(mock_client):
    """OpenAI API failure raises EmbeddingError"""
    mock_client.embeddings.create.side_effect = Exception("API error")
    
    with pytest.raises(EmbeddingError, match="Failed to generate query embedding"):
        embed_query("Test query")


@patch('services.embedder.client')
def test_embed_chunks_rate_limit(mock_client):
    """OpenAI 429 raises RateLimitError"""
    mock_client.embeddings.create.side_effect = _openai_rate_limit_error()

    with pytest.raises(RateLimitError, match="rate limited"):
        embed_chunks(["Test chunk"])


@patch('services.embedder.client')
def test_embed_query_rate_limit(mock_client):
    """OpenAI 429 raises RateLimitError"""
    mock_client.embeddings.create.side_effect = _openai_rate_limit_error()

    with pytest.raises(RateLimitError, match="rate limited"):
        embed_query("Test query")
