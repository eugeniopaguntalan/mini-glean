"""
Pydantic Schemas
Request and response models for API endpoints
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field


class DocumentResponse(BaseModel):
    """Response model for a single document"""
    id: str
    filename: str
    type: str  # 'pdf', 'url', or 'note'
    tags: List[str]
    chunk_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Response model for list of documents"""
    documents: List[DocumentResponse]
    total: int


class UrlIngestRequest(BaseModel):
    """Request model for URL ingestion"""
    url: HttpUrl


class NoteIngestRequest(BaseModel):
    """Request model for note ingestion"""
    content: str = Field(..., min_length=1)
    tags: Optional[List[str]] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str
    code: str
