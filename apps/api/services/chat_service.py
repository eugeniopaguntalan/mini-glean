"""
Chat Service
Orchestrates the RAG pipeline: retrieve → format → generate → respond
"""

from datetime import datetime, UTC
from typing import List
import uuid
from repositories.chunk_repository import ChunkRepository
from services import retriever, llm
from schemas import ChatResponse, SourceCitation


async def ask(question: str, chunk_repo: ChunkRepository) -> ChatResponse:
    """
    Answer a question using RAG pipeline
    
    Args:
        question: The user's question
        chunk_repo: Repository for chunk database access
        
    Returns:
        ChatResponse with answer and source citations
    """
    # Retrieve relevant chunks
    chunks = await retriever.retrieve(question, chunk_repo, top_k=5)
    
    # If no relevant chunks found, return refusal
    if not chunks:
        return ChatResponse(
            id=str(uuid.uuid4()),
            content="I don't have that in my knowledge base.",
            sources=[],
            created_at=datetime.now(UTC).isoformat()
        )
    
    # Format chunks into context string
    context = _format_context(chunks)
    
    # Generate answer using LLM
    answer = llm.generate_answer(question, context)
    
    # Extract unique source documents
    sources = _extract_sources(chunks)
    
    return ChatResponse(
        id=str(uuid.uuid4()),
        content=answer,
        sources=sources,
        created_at=datetime.now(UTC).isoformat()
    )


def _format_context(chunks: List[retriever.RetrievedChunk]) -> str:
    """
    Format retrieved chunks into context string for LLM
    
    Format:
        [source: doc_id | filename]
        content
        
        ---
        
        [source: doc_id | filename]
        content
    """
    formatted = []
    for chunk in chunks:
        formatted.append(
            f"[source: {chunk.document_id} | {chunk.filename}]\n{chunk.content}"
        )
    
    return "\n\n---\n\n".join(formatted)


def _extract_sources(chunks: List[retriever.RetrievedChunk]) -> List[SourceCitation]:
    """
    Extract unique source documents from chunks
    
    - Deduplicate by document_id
    - Include excerpt from most relevant chunk per document
    - Order by highest similarity first
    """
    # Group chunks by document_id, keeping only the highest similarity chunk per doc
    doc_map = {}
    for chunk in chunks:
        if chunk.document_id not in doc_map or chunk.similarity > doc_map[chunk.document_id].similarity:
            doc_map[chunk.document_id] = chunk
    
    # Convert to SourceCitation objects
    sources = []
    for doc_id, chunk in doc_map.items():
        # Take first 100 characters as excerpt
        excerpt = chunk.content[:100]
        if len(chunk.content) > 100:
            excerpt += "..."
        
        sources.append(SourceCitation(
            doc_id=doc_id,
            filename=chunk.filename,
            excerpt=excerpt
        ))
    
    # Sort by similarity (highest first)
    # We need to get back to the chunks to get similarity
    sources.sort(
        key=lambda s: doc_map[s.doc_id].similarity,
        reverse=True
    )
    
    return sources
