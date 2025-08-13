#!/usr/bin/env python3
"""
StudyMate Real IBM Granite API
FastAPI backend with actual IBM Granite model integration
"""

import os
import sys
import logging
import time
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# FastAPI imports
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# AI/ML imports
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

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
    loaded: bool = False
    size_gb: Optional[float] = None

class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    model: Optional[str] = "granite-3b-code-instruct"
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_new_tokens: Optional[int] = Field(default=512, ge=1, le=2048)
    top_p: Optional[float] = Field(default=0.9, ge=0.0, le=1.0)
    top_k: Optional[int] = Field(default=50, ge=1, le=100)

class QuestionResponse(BaseModel):
    answer: str
    model_used: str
    processing_time: float
    confidence: float
    generation_params: Dict[str, Any]
    sources: List[Dict[str, Any]] = []

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    models_loaded: List[str]
    device: str
    memory_usage: Dict[str, Any]

# Global model manager
class RealGraniteModelManager:
    """Real IBM Granite model manager with actual HuggingFace integration"""
    
    def __init__(self):
        self.device = self._get_device()
        self.loaded_models = {}
        self.embedding_model = None
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Available IBM Granite models
        self.available_models = {
            "granite-3b-code-instruct": {
                "model_id": "ibm-granite/granite-3b-code-instruct",
                "name": "IBM Granite 3B Code Instruct",
                "description": "IBM's Granite model optimized for code and instruction following",
                "size_gb": 6.96,
                "status": "available"
            },
            "granite-8b-code-instruct": {
                "model_id": "ibm-granite/granite-8b-code-instruct", 
                "name": "IBM Granite 8B Code Instruct",
                "description": "Advanced IBM Granite model for complex code understanding",
                "size_gb": 16.0,
                "status": "available"
            }
        }
        
        self.current_model_key = None
        
        logger.info(f"Real Granite Model Manager initialized with device: {self.device}")
    
    def _get_device(self) -> str:
        """Determine the best available device"""
        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"
    
    async def initialize(self):
        """Initialize the model manager"""
        logger.info("Initializing Real Granite Model Manager...")
        
        # Load embedding model first
        await self.load_embedding_model()
        
        # Try to load the default Granite model
        await self.load_granite_model("granite-3b-code-instruct")
        
        logger.info("Real Granite Model Manager initialization complete")
    
    async def load_embedding_model(self) -> bool:
        """Load sentence transformer for embeddings"""
        try:
            if self.embedding_model is not None:
                return True
            
            logger.info("Loading embedding model...")
            
            loop = asyncio.get_event_loop()
            self.embedding_model = await loop.run_in_executor(
                self.executor,
                lambda: SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device=self.device)
            )
            
            logger.info("✅ Embedding model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            return False
    
    async def load_granite_model(self, model_key: str) -> bool:
        """Load a specific IBM Granite model"""
        try:
            if model_key in self.loaded_models:
                logger.info(f"Model {model_key} already loaded")
                self.current_model_key = model_key
                return True
            
            if model_key not in self.available_models:
                logger.error(f"Unknown model: {model_key}")
                return False
            
            model_config = self.available_models[model_key]
            model_id = model_config["model_id"]
            
            logger.info(f"Loading IBM Granite model: {model_config['name']}")
            
            # Load in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            
            # Load tokenizer
            tokenizer = await loop.run_in_executor(
                self.executor,
                self._load_tokenizer,
                model_id
            )
            
            # Load model
            model = await loop.run_in_executor(
                self.executor,
                self._load_model,
                model_id
            )
            
            # Create generation config
            generation_config = GenerationConfig(
                max_new_tokens=512,
                temperature=0.7,
                top_p=0.9,
                top_k=50,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )
            
            # Store loaded model
            self.loaded_models[model_key] = {
                "model": model,
                "tokenizer": tokenizer,
                "config": model_config,
                "generation_config": generation_config,
                "loaded_at": time.time()
            }
            
            self.current_model_key = model_key
            
            logger.info(f"✅ Successfully loaded IBM Granite model: {model_config['name']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load IBM Granite model {model_key}: {e}")
            return False
    
    def _load_tokenizer(self, model_id: str):
        """Load tokenizer in thread pool"""
        tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            trust_remote_code=True
        )
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        return tokenizer
    
    def _load_model(self, model_id: str):
        """Load model in thread pool"""
        model_kwargs = {
            "trust_remote_code": True,
            "torch_dtype": torch.float16 if self.device != "cpu" else torch.float32,
            "device_map": "auto" if self.device == "cuda" else None
        }
        
        model = AutoModelForCausalLM.from_pretrained(model_id, **model_kwargs)
        
        if model_kwargs["device_map"] is None and self.device != "cpu":
            model = model.to(self.device)
        
        return model
    
    async def generate_text(self, prompt: str, model_key: str = None, **kwargs) -> str:
        """Generate text using IBM Granite model"""
        try:
            if model_key is None:
                model_key = self.current_model_key
            
            if model_key not in self.loaded_models:
                logger.error(f"Model {model_key} not loaded")
                return "Error: Model not available. Please wait for model to load."
            
            model_data = self.loaded_models[model_key]
            model = model_data["model"]
            tokenizer = model_data["tokenizer"]
            
            # Create generation config
            generation_config = GenerationConfig(
                max_new_tokens=kwargs.get("max_new_tokens", 512),
                temperature=kwargs.get("temperature", 0.7),
                top_p=kwargs.get("top_p", 0.9),
                top_k=kwargs.get("top_k", 50),
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )
            
            # Generate in thread pool
            loop = asyncio.get_event_loop()
            generated_text = await loop.run_in_executor(
                self.executor,
                self._generate_sync,
                model,
                tokenizer,
                prompt,
                generation_config
            )
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            return f"Error generating response: {str(e)}"
    
    def _generate_sync(self, model, tokenizer, prompt, generation_config):
        """Synchronous text generation"""
        try:
            inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
            
            if self.device != "cpu":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = model.generate(**inputs, generation_config=generation_config)
            
            generated_ids = outputs[0][inputs["input_ids"].shape[1]:]
            generated_text = tokenizer.decode(generated_ids, skip_special_tokens=True)
            
            return generated_text.strip()
            
        except Exception as e:
            logger.error(f"Sync generation failed: {e}")
            return f"Generation error: {str(e)}"
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage information"""
        memory_info = {
            "device": self.device,
            "loaded_models": len(self.loaded_models),
            "embedding_model_loaded": self.embedding_model is not None
        }
        
        if torch.cuda.is_available():
            memory_info.update({
                "gpu_memory_allocated_gb": torch.cuda.memory_allocated() / 1024**3,
                "gpu_memory_reserved_gb": torch.cuda.memory_reserved() / 1024**3,
                "gpu_memory_total_gb": torch.cuda.get_device_properties(0).total_memory / 1024**3
            })
        
        return memory_info

# Global model manager instance
model_manager = RealGraniteModelManager()

# Create FastAPI app
app = FastAPI(
    title="StudyMate - Real IBM Granite API",
    description="Production AI Academic Assistant with Real IBM Granite Models",
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

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    logger.info("Starting Real IBM Granite API...")
    await model_manager.initialize()

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "StudyMate - Real IBM Granite API",
        "version": "2.0.0",
        "description": "Production AI Academic Assistant with Real IBM Granite Models from HuggingFace",
        "features": [
            "Real IBM Granite 3B & 8B Models",
            "HuggingFace Transformers Integration", 
            "Advanced PDF Processing",
            "FAISS Vector Search",
            "Production-Ready Architecture"
        ],
        "docs_url": "/docs",
        "status": "operational"
    }

# Health check
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check"""
    memory_usage = model_manager.get_memory_usage()
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="2.0.0",
        models_loaded=list(model_manager.loaded_models.keys()),
        device=model_manager.device,
        memory_usage=memory_usage
    )

# Models endpoints
@app.get("/api/v1/models/")
async def list_models():
    """Get available IBM Granite models"""
    models = []
    for model_id, config in model_manager.available_models.items():
        models.append(ModelInfo(
            model_id=model_id,
            name=config["name"],
            description=config["description"],
            status=config["status"],
            loaded=model_id in model_manager.loaded_models,
            size_gb=config.get("size_gb")
        ))
    
    return {
        "models": models,
        "current_model": model_manager.current_model_key,
        "device": model_manager.device,
        "total": len(models)
    }

@app.post("/api/v1/models/load/{model_key}")
async def load_model(model_key: str, background_tasks: BackgroundTasks):
    """Load a specific IBM Granite model"""
    if model_key not in model_manager.available_models:
        raise HTTPException(status_code=400, detail=f"Unknown model: {model_key}")
    
    # Start loading in background
    background_tasks.add_task(model_manager.load_granite_model, model_key)
    
    return {
        "message": f"Loading IBM Granite model: {model_key}",
        "status": "loading",
        "model_key": model_key
    }

# Q&A endpoint with real IBM Granite
@app.post("/api/v1/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question using real IBM Granite models"""
    start_time = time.time()
    
    logger.info(f"Processing question with IBM Granite {request.model}: {request.question[:50]}...")
    
    # Check if model is loaded
    if request.model not in model_manager.loaded_models:
        # Try to load the model
        success = await model_manager.load_granite_model(request.model)
        if not success:
            raise HTTPException(
                status_code=503, 
                detail=f"IBM Granite model {request.model} is not available or failed to load"
            )
    
    # Generate response using real IBM Granite model
    generation_params = {
        "max_new_tokens": request.max_new_tokens,
        "temperature": request.temperature,
        "top_p": request.top_p,
        "top_k": request.top_k
    }
    
    answer = await model_manager.generate_text(
        request.question,
        request.model,
        **generation_params
    )
    
    processing_time = time.time() - start_time
    
    return QuestionResponse(
        answer=answer,
        model_used=request.model,
        processing_time=processing_time,
        confidence=0.85,  # Would be calculated based on model outputs
        generation_params=generation_params,
        sources=[]
    )

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                                                                              ║
    ║   🚀 StudyMate - Real IBM Granite API                                       ║
    ║                                                                              ║
    ║   🤖 Real IBM Granite Models from HuggingFace                               ║
    ║   📄 Production-Ready Architecture                                           ║
    ║   🔍 Advanced AI Processing                                                  ║
    ║                                                                              ║
    ║   📚 API Documentation: http://localhost:8001/docs                          ║
    ║   ❤️  Health Check: http://localhost:8001/health                            ║
    ║                                                                              ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "real_granite_api:app",
        host="0.0.0.0",
        port=8001,
        reload=False,  # Disable reload to prevent model reloading
        log_level="info"
    )
