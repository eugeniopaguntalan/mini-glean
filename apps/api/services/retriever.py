"""
Retriever Service
Combines embedding + vector search for document retrieval
"""

from dataclasses import dataclass
from typing import List
from services.embedder import embed_query
from repositories.chunk_repository import ChunkRepository


# Similarity threshold - chunks below this are considered irrelevant
SIMILARITY_THRESHOLD = 0.3


@dataclass
class RetrievedChunk:
    """A single retrieved chunk with metadata"""
    chunk_id: str
    content: str
    document_id: str
    filename: str
    similarity: float


async def retrieve(question: str, chunk_repo: ChunkRepository, top_k: int = 5) -> List[RetrievedChunk]:
    """
    Retrieve relevant chunks for a question
    
    Args:
        question: The user's question
        chunk_repo: Repository for chunk database access
        top_k: Maximum number of chunks to retrieve
        
    Returns:
        List of RetrievedChunk objects (may be empty)
        Chunks are filtered by similarity threshold
    """
    # Embed the question
    query_embedding = embed_query(question)
    
    # Search for similar chunks
    results = await chunk_repo.search_similar(query_embedding, top_k)
    
    # Convert distance to similarity (cosine distance: 0=identical, 2=opposite)
    # similarity = 1 - distance
    # Filter by threshold
    chunks = []
    for result in results:
        similarity = 1.0 - result["distance"]
        
        # Only include chunks above threshold
        if similarity > SIMILARITY_THRESHOLD:
            chunks.append(RetrievedChunk(
                chunk_id=result["id"],
                content=result["content"],
                document_id=result["document_id"],
                filename=result["filename"],
                similarity=similarity
            ))
    
    return chunks
