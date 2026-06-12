"""
Document Repository
Database access layer for Document operations
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models import Document


class DocumentRepository:
    """Repository for Document CRUD operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, filename: str, doc_type: str, tags: List[str] = None) -> Document:
        """Create a new document"""
        document = Document(
            filename=filename,
            type=doc_type,
            tags=tags or [],
        )
        self.session.add(document)
        await self.session.commit()
        await self.session.refresh(document)
        return document
    
    async def get_by_id(self, doc_id: str) -> Optional[Document]:
        """Get a document by ID"""
        result = await self.session.execute(
            select(Document).where(Document.id == doc_id)
        )
        return result.scalar_one_or_none()
    
    async def list_all(self) -> List[Document]:
        """List all documents"""
        result = await self.session.execute(
            select(Document).order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def count(self) -> int:
        """Count total documents"""
        result = await self.session.execute(
            select(func.count(Document.id))
        )
        return result.scalar_one()
    
    async def delete(self, doc_id: str) -> bool:
        """Delete a document by ID"""
        document = await self.get_by_id(doc_id)
        if document:
            await self.session.delete(document)
            await self.session.commit()
            return True
        return False
