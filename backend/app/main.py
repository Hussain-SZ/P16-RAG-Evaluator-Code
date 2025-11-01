from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.app.api.api import api_router
from backend.app.config.settings import settings
from backend.app.database.connection import db_manager
from backend.app.utils.helpers import setup_logging
import logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting RAG Evaluator API...")
    
    # Connect to database
    try:
        db_manager.connect()
        logger.info("✅ Database connected successfully")
    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {e}")
        raise e
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down RAG Evaluator API...")
    db_manager.disconnect()

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="RAG Evaluator API for evaluating Retrieval-Augmented Generation systems",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Include legacy routes for backward compatibility with frontend
from backend.app.api.auth_legacy import router as auth_legacy_router
app.include_router(auth_legacy_router, prefix="/auth", tags=["Legacy Auth"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to RAG Evaluator API",
        "version": settings.version,
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "database": "connected" if db_manager.is_connected() else "disconnected"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
