"""
Embedder Service
Generates vector embeddings using OpenAI
"""

from typing import List
from openai import OpenAI, RateLimitError as OpenAIRateLimitError
from config import settings
from services.exceptions import EmbeddingError, RateLimitError


# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)


def embed_chunks(chunks: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of text chunks
    
    Args:
        chunks: List of text strings to embed
        
    Returns:
        List of 1536-dimension embedding vectors
        
    Raises:
        EmbeddingError: If the OpenAI API call fails
    """
    if not chunks:
        return []
    
    try:
        # Process in batches of 20 to stay under rate limits
        batch_size = 20
        all_embeddings = []
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            # Call OpenAI embeddings API
            response = client.embeddings.create(
                model=settings.EMBEDDING_MODEL,
                input=batch
            )
            
            # Extract embeddings from response
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings
        
    except OpenAIRateLimitError as e:
        raise RateLimitError(f"Embedding service rate limited: {str(e)}")
    except Exception as e:
        raise EmbeddingError(f"Failed to generate embeddings: {str(e)}")


def embed_query(query: str) -> List[float]:
    """
    Generate embedding for a single query string
    
    Args:
        query: Text query to embed
        
    Returns:
        1536-dimension embedding vector
        
    Raises:
        EmbeddingError: If the OpenAI API call fails
    """
    try:
        response = client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=[query]
        )
        
        return response.data[0].embedding
        
    except OpenAIRateLimitError as e:
        raise RateLimitError(f"Embedding service rate limited: {str(e)}")
    except Exception as e:
        raise EmbeddingError(f"Failed to generate query embedding: {str(e)}")
