"""
Main FastAPI application for Deep Chatbot.

Clean Architecture implementation with proper separation of concerns.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ...infrastructure.persistence.sqlalchemy.base import close_database, init_database
from .v1.routes import conversation_router, memory_router, planning_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup: Initialize database
    print("🚀 Initializing database...")
    await init_database()
    print("✅ Database initialized")

    yield

    # Shutdown: Close database connections
    print("🛑 Closing database connections...")
    await close_database()
    print("✅ Database connections closed")


# Create FastAPI application
app = FastAPI(
    title="Deep Chatbot API",
    description="Deep agent chatbot with Clean Architecture",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(conversation_router, prefix="/api/v1")
app.include_router(planning_router, prefix="/api/v1")
app.include_router(memory_router, prefix="/api/v1")


# Root endpoint
@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": "Deep Chatbot API",
        "version": "2.0.0",
        "architecture": "Clean Architecture + Screaming Architecture",
        "endpoints": {
            "conversation": "/api/v1/conversations",
            "planning": "/api/v1/plans",
            "memory": "/api/v1/memory",
            "docs": "/docs",
        },
    }


# Health check
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "architecture": "Clean Architecture",
    }
