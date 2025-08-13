#!/usr/bin/env python3
"""
StudyMate Test API - Simplified version for demonstration
Shows IBM Granite integration with FastAPI
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# FastAPI imports
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models
class ModelInfo(BaseModel):
    model_id: str
    name: str
    description: str
    status: str

class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    model: Optional[str] = "granite-3b-code-instruct"
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=512, ge=1, le=2048)

class QuestionResponse(BaseModel):
    answer: str
    model_used: str
    processing_time: float
    confidence: float
    sources: List[Dict[str, Any]] = []

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    models_available: List[str]

# Create FastAPI app
app = FastAPI(
    title="StudyMate API - IBM Granite Integration",
    description="Advanced AI Academic Assistant with IBM Granite Models",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
class AppState:
    def __init__(self):
        self.models_loaded = False
        self.current_model = "granite-3b-code-instruct"
        self.available_models = {
            "granite-3b-code-instruct": {
                "name": "IBM Granite 3B Code Instruct",
                "description": "IBM's Granite model optimized for code and instruction following",
                "status": "available"
            },
            "granite-8b-code-instruct": {
                "name": "IBM Granite 8B Code Instruct", 
                "description": "Advanced IBM Granite model for complex code understanding",
                "status": "available"
            },
            "granite-13b-instruct": {
                "name": "IBM Granite 13B Instruct",
                "description": "Large IBM Granite model for advanced reasoning",
                "status": "available"
            }
        }
        self.documents = []
        self.conversations = []

app_state = AppState()

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "StudyMate API",
        "version": "2.0.0",
        "description": "Advanced AI Academic Assistant with IBM Granite Integration",
        "features": [
            "IBM Granite Models from HuggingFace",
            "Advanced PDF Processing",
            "FAISS Vector Search",
            "JWT Authentication",
            "Real-time Q&A"
        ],
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "status": "operational"
    }

# Health check
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="2.0.0",
        models_available=list(app_state.available_models.keys())
    )

# Models endpoints
@app.get("/api/v1/models/")
async def list_models():
    """Get list of available IBM Granite models"""
    models = []
    for model_id, config in app_state.available_models.items():
        models.append(ModelInfo(
            model_id=model_id,
            name=config["name"],
            description=config["description"],
            status=config["status"]
        ))
    
    return {
        "models": models,
        "current_model": app_state.current_model,
        "total": len(models)
    }

@app.get("/api/v1/models/current")
async def get_current_model():
    """Get current model information"""
    if app_state.current_model in app_state.available_models:
        config = app_state.available_models[app_state.current_model]
        return {
            "model_id": app_state.current_model,
            "name": config["name"],
            "description": config["description"],
            "status": config["status"],
            "loaded": app_state.models_loaded
        }
    else:
        raise HTTPException(status_code=404, detail="Current model not found")

@app.post("/api/v1/models/switch")
async def switch_model(model_id: str):
    """Switch to a different IBM Granite model"""
    if model_id not in app_state.available_models:
        raise HTTPException(
            status_code=400, 
            detail=f"Unknown model: {model_id}. Available models: {list(app_state.available_models.keys())}"
        )
    
    app_state.current_model = model_id
    logger.info(f"Switched to model: {model_id}")
    
    return {
        "success": True,
        "message": f"Successfully switched to {app_state.available_models[model_id]['name']}",
        "current_model": model_id
    }

# Q&A endpoint (simulated for demonstration)
@app.post("/api/v1/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question using IBM Granite models"""
    import time
    start_time = time.time()
    
    # Simulate model processing
    logger.info(f"Processing question with {request.model}: {request.question[:50]}...")
    
    # Simulated response (in real implementation, this would use the actual Granite model)
    simulated_answer = f"""Based on the IBM Granite {request.model} model analysis:

This is a simulated response demonstrating the StudyMate API architecture. In the full implementation, this would be processed by the actual IBM Granite model from HuggingFace.

Key features of this API:
- FastAPI backend with async support
- IBM Granite model integration via HuggingFace
- FAISS vector database for document search
- JWT authentication system
- Comprehensive monitoring and analytics

Your question: "{request.question}"

The system would analyze your uploaded documents using FAISS vector search, then generate a contextual response using the selected IBM Granite model with the specified parameters (temperature: {request.temperature}, max_tokens: {request.max_tokens}).
"""
    
    processing_time = time.time() - start_time
    
    return QuestionResponse(
        answer=simulated_answer,
        model_used=request.model,
        processing_time=processing_time,
        confidence=0.85,
        sources=[]
    )

# Document upload endpoint (simulated)
@app.post("/api/v1/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF document for processing"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Simulate document processing
    document_info = {
        "id": len(app_state.documents) + 1,
        "filename": file.filename,
        "size": file.size if hasattr(file, 'size') else 0,
        "status": "processed",
        "uploaded_at": datetime.now().isoformat(),
        "pages": 10,  # Simulated
        "chunks": 25  # Simulated
    }
    
    app_state.documents.append(document_info)
    
    return {
        "success": True,
        "message": f"Document {file.filename} uploaded and processed successfully",
        "document": document_info
    }

# Documents list endpoint
@app.get("/api/v1/documents/")
async def list_documents():
    """Get list of uploaded documents"""
    return {
        "documents": app_state.documents,
        "total": len(app_state.documents)
    }

# Analytics endpoint
@app.get("/api/v1/analytics/")
async def get_analytics():
    """Get system analytics"""
    return {
        "documents": {
            "total": len(app_state.documents),
            "total_pages": sum(doc.get("pages", 0) for doc in app_state.documents),
            "total_chunks": sum(doc.get("chunks", 0) for doc in app_state.documents)
        },
        "models": {
            "available": len(app_state.available_models),
            "current": app_state.current_model,
            "loaded": app_state.models_loaded
        },
        "conversations": {
            "total": len(app_state.conversations)
        }
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                                                                              ║
    ║   🚀 StudyMate Test API - IBM Granite Integration Demo                      ║
    ║                                                                              ║
    ║   🤖 IBM Granite Models (Simulated)                                         ║
    ║   📄 Document Processing                                                     ║
    ║   🔍 Q&A System                                                              ║
    ║   📊 Analytics Dashboard                                                     ║
    ║                                                                              ║
    ║   📚 API Documentation: http://localhost:8000/docs                          ║
    ║   🔄 ReDoc: http://localhost:8000/redoc                                     ║
    ║   ❤️  Health Check: http://localhost:8000/health                            ║
    ║                                                                              ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "test_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
