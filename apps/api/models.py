"""
SQLAlchemy Models
Document and Chunk tables with pgvector support
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from database import Base
import uuid


def generate_uuid():
    """Generate a UUID string for primary keys"""
    return str(uuid.uuid4())


class Document(Base):
    """Document model - represents an uploaded PDF, URL, or note"""
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    filename = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'pdf', 'url', or 'note'
    tags = Column(ARRAY(String), default=list)
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to chunks with cascade delete
    chunks = relationship(
        "Chunk",
        back_populates="document",
        cascade="all, delete-orphan",
    )


class Chunk(Base):
    """Chunk model - represents a text chunk with its embedding vector"""
    __tablename__ = "chunks"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536))  # OpenAI text-embedding-3-small dimension
    chunk_index = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to document
    document = relationship("Document", back_populates="chunks")
