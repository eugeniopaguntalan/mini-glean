"""
FastAPI Application
Main entry point for the MiniGlean API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text
from config import settings
from database import engine
from routers import health, documents


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events
    Verifies database connection on startup
    """
    # Startup: verify database connection
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        print(f"✓ Database connected successfully")
        print(f"✓ Environment: {settings.ENVIRONMENT}")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
    
    yield
    
    # Shutdown: cleanup
    await engine.dispose()


# Create FastAPI app
app = FastAPI(
    title="MiniGlean API",
    description="Personal knowledge base with AI-powered search",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(documents.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MiniGlean API",
        "version": "0.1.0",
        "docs": "/docs",
    }
