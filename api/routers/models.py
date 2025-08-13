"""
Models API router for StudyMate
IBM Granite model management endpoints
"""

import logging
import time
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_db
from ..auth.auth import get_current_active_user
from ..models.database import User
from ..schemas.schemas import (
    ModelInfo,
    ModelListResponse,
    ModelSwitchRequest,
    QuestionRequest,
    QuestionResponse,
    ErrorResponse
)
from ..services.model_service import model_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=ModelListResponse)
async def list_models(
    current_user: User = Depends(get_current_active_user)
):
    """Get list of available IBM Granite models"""
    try:
        from ..config import settings
        
        # Get available models
        models = []
        for key, config in settings.granite_models.items():
            model_info = ModelInfo(
                model_id=key,
                name=config["name"],
                description=config["description"],
                max_length=config["max_length"],
                default_params={
                    "temperature": config["temperature"],
                    "top_p": config["top_p"],
                    "top_k": config["top_k"]
                }
            )
            models.append(model_info)
        
        # Get current model
        current_model_info = await model_service.get_current_model_info()
        current_model = current_model_info["key"] if current_model_info else settings.default_granite_model
        
        return ModelListResponse(
            models=models,
            current_model=current_model
        )
        
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve model list"
        )

@router.get("/current")
async def get_current_model(
    current_user: User = Depends(get_current_active_user)
):
    """Get information about the currently loaded model"""
    try:
        model_info = await model_service.get_current_model_info()
        
        if not model_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No model currently loaded"
            )
        
        return model_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get current model info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve current model information"
        )

@router.post("/switch")
async def switch_model(
    request: ModelSwitchRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Switch to a different IBM Granite model"""
    try:
        # Validate model exists
        from ..config import settings
        if request.model not in settings.granite_models:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown model: {request.model}"
            )
        
        # Switch model
        success = await model_service.switch_model(request.model)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to switch to model: {request.model}"
            )
        
        # Update user preference
        current_user.preferred_model = request.model
        await db.commit()
        
        # Get updated model info
        model_info = await model_service.get_current_model_info()
        
        return {
            "success": True,
            "message": f"Successfully switched to {model_info['name']}",
            "model_info": model_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to switch model: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to switch model"
        )

@router.get("/loaded")
async def get_loaded_models(
    current_user: User = Depends(get_current_active_user)
):
    """Get list of currently loaded models"""
    try:
        loaded_models = await model_service.get_loaded_models()
        
        return {
            "loaded_models": loaded_models,
            "count": len(loaded_models)
        }
        
    except Exception as e:
        logger.error(f"Failed to get loaded models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve loaded models"
        )

@router.get("/memory")
async def get_memory_usage(
    current_user: User = Depends(get_current_active_user)
):
    """Get model memory usage information"""
    try:
        memory_info = await model_service.get_memory_usage()
        
        return memory_info
        
    except Exception as e:
        logger.error(f"Failed to get memory usage: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve memory usage information"
        )

@router.post("/generate")
async def generate_text(
    request: QuestionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Generate text using the current IBM Granite model"""
    try:
        # Validate model
        model_key = request.model if request.model else None
        
        # Prepare generation parameters
        generation_params = {
            "max_new_tokens": request.max_new_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "top_k": request.top_k
        }
        
        # Generate text
        start_time = time.time()
        generated_text = await model_service.generate_text(
            prompt=request.question,
            model_key=model_key,
            **generation_params
        )
        processing_time = time.time() - start_time
        
        # Get current model info
        model_info = await model_service.get_current_model_info()
        model_used = model_info["key"] if model_info else "unknown"
        
        return {
            "generated_text": generated_text,
            "model_used": model_used,
            "processing_time": processing_time,
            "generation_params": generation_params
        }
        
    except Exception as e:
        logger.error(f"Text generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text generation failed: {str(e)}"
        )

@router.post("/reload/{model_key}")
async def reload_model(
    model_key: str,
    current_user: User = Depends(get_current_active_user)
):
    """Reload a specific model (admin function)"""
    try:
        # Check if user has permission (could add admin check here)
        from ..config import settings
        if model_key not in settings.granite_models:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown model: {model_key}"
            )
        
        # Clear the model if loaded
        if model_key in model_service.loaded_models:
            del model_service.loaded_models[model_key]
        
        # Reload the model
        success = await model_service.load_granite_model(model_key)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to reload model: {model_key}"
            )
        
        return {
            "success": True,
            "message": f"Successfully reloaded model: {model_key}",
            "model_key": model_key
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reload model {model_key}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reload model"
        )

@router.get("/health")
async def model_health_check():
    """Check model service health"""
    try:
        # Check if embedding model is loaded
        embedding_loaded = model_service.embedding_model is not None
        
        # Check loaded models
        loaded_models = await model_service.get_loaded_models()
        
        # Get memory usage
        memory_info = await model_service.get_memory_usage()
        
        # Determine health status
        status_healthy = embedding_loaded and len(loaded_models) > 0
        
        return {
            "status": "healthy" if status_healthy else "degraded",
            "embedding_model_loaded": embedding_loaded,
            "loaded_models": loaded_models,
            "model_count": len(loaded_models),
            "memory_info": memory_info,
            "device": model_service.device
        }
        
    except Exception as e:
        logger.error(f"Model health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
