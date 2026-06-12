"""
Health Check Router
Verifies database connectivity and system status
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database import get_session
from config import settings

router = APIRouter()


@router.get("/health")
async def health_check(session: AsyncSession = Depends(get_session)):
    """
    Health check endpoint
    Returns system status and database connectivity
    """
    try:
        # Attempt a simple query to verify database connection
        result = await session.execute(text("SELECT 1"))
        result.scalar()
        
        return {
            "status": "ok",
            "database": "connected",
            "environment": settings.ENVIRONMENT,
        }
    except Exception as e:
        return {
            "status": "degraded",
            "database": "disconnected",
            "environment": settings.ENVIRONMENT,
            "error": str(e),
        }
