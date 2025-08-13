"""
StudyMate Advanced API with IBM Granite Integration
FastAPI backend with comprehensive REST endpoints
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
import uvicorn

# Import configurations and dependencies
from .config import settings
from .database import engine, get_db
from .models.database import Base
from .schemas.schemas import HealthResponse, ErrorResponse

# Import routers
from .routers import (
    auth,
    users,
    documents,
    conversations,
    models,
    search,
    analytics,
    admin
)

# Import middleware and utilities
from .middleware.rate_limiting import RateLimitMiddleware
from .middleware.logging import LoggingMiddleware
from .middleware.metrics import MetricsMiddleware
from .utils.exceptions import setup_exception_handlers

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=settings.log_format
)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting StudyMate API...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize models
    from .services.model_service import model_service
    await model_service.initialize()
    
    # Initialize vector database
    from .services.vector_service import vector_service
    await vector_service.initialize()
    
    logger.info("StudyMate API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down StudyMate API...")
    
    # Cleanup models
    await model_service.cleanup()
    
    # Close database connections
    await engine.dispose()
    
    logger.info("StudyMate API shutdown complete")

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers,
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure based on deployment
)

if settings.enable_metrics:
    app.add_middleware(MetricsMiddleware)

app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# Setup exception handlers
setup_exception_handlers(app)

# Include routers
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

app.include_router(
    users.router,
    prefix="/api/v1/users",
    tags=["Users"]
)

app.include_router(
    documents.router,
    prefix="/api/v1/documents",
    tags=["Documents"]
)

app.include_router(
    conversations.router,
    prefix="/api/v1/conversations",
    tags=["Conversations"]
)

app.include_router(
    models.router,
    prefix="/api/v1/models",
    tags=["Models"]
)

app.include_router(
    search.router,
    prefix="/api/v1/search",
    tags=["Search"]
)

app.include_router(
    analytics.router,
    prefix="/api/v1/analytics",
    tags=["Analytics"]
)

app.include_router(
    admin.router,
    prefix="/api/v1/admin",
    tags=["Administration"]
)

# Static files (for uploaded documents, exports, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Root endpoints
@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": settings.app_description,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "status": "operational"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        from .database import get_db
        db = next(get_db())
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    # Check model service
    try:
        from .services.model_service import model_service
        models_loaded = await model_service.get_loaded_models()
        model_status = "healthy"
    except Exception as e:
        logger.error(f"Model service health check failed: {e}")
        models_loaded = []
        model_status = "unhealthy"
    
    # Calculate uptime (simplified)
    uptime = time.time() - getattr(app.state, 'start_time', time.time())
    
    return HealthResponse(
        status="healthy" if db_status == "healthy" and model_status == "healthy" else "degraded",
        timestamp=time.time(),
        version=settings.app_version,
        database=db_status,
        models_loaded=models_loaded,
        uptime=uptime
    )

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    if not settings.enable_metrics:
        raise HTTPException(status_code=404, detail="Metrics not enabled")
    
    from .middleware.metrics import get_metrics
    return get_metrics()

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            error_code=f"HTTP_{exc.status_code}"
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc) if settings.debug else None,
            error_code="INTERNAL_ERROR"
        ).dict()
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    app.state.start_time = time.time()
    logger.info(f"StudyMate API v{settings.app_version} starting up...")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("StudyMate API shutting down...")

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
        access_log=True
    )
