"""
Chunk Repository
Database access layer for Chunk operations with vector similarity search
"""

from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, text
from models import Chunk


class ChunkRepository:
    """Repository for Chunk CRUD and vector search operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def add_chunks(self, chunks: List[Chunk]) -> None:
        """Add multiple chunks to the database"""
        self.session.add_all(chunks)
        await self.session.commit()
    
    async def search_similar(self, embedding: List[float], top_k: int = 5) -> List[Dict]:
        """
        Search for similar chunks using vector similarity
        Returns chunks with document metadata
        """
        # Use pgvector's <=> operator for cosine distance
        query = text("""
            SELECT 
                c.id,
                c.content,
                c.chunk_index,
                c.embedding <=> :embedding::vector AS distance,
                d.id AS document_id,
                d.filename,
                d.type
            FROM chunks c
            JOIN documents d ON c.document_id = d.id
            ORDER BY c.embedding <=> :embedding::vector
            LIMIT :top_k
        """)
        
        result = await self.session.execute(
            query,
            {"embedding": str(embedding), "top_k": top_k}
        )
        
        rows = result.fetchall()
        return [
            {
                "id": row.id,
                "content": row.content,
                "chunk_index": row.chunk_index,
                "distance": float(row.distance),
                "document_id": row.document_id,
                "filename": row.filename,
                "type": row.type,
            }
            for row in rows
        ]
    
    async def get_by_document_id(self, doc_id: str) -> List[Chunk]:
        """Get all chunks for a specific document"""
        result = await self.session.execute(
            select(Chunk)
            .where(Chunk.document_id == doc_id)
            .order_by(Chunk.chunk_index)
        )
        return list(result.scalars().all())
    
    async def delete_by_document_id(self, doc_id: str) -> int:
        """Delete all chunks for a specific document"""
        result = await self.session.execute(
            delete(Chunk).where(Chunk.document_id == doc_id)
        )
        await self.session.commit()
        return result.rowcount
