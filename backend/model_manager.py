"""
Advanced IBM Granite Model Manager for StudyMate API
Specialized integration with IBM Granite models from HuggingFace
"""

import torch
import asyncio
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    pipeline,
    BitsAndBytesConfig,
    GenerationConfig
)
from sentence_transformers import SentenceTransformer
import gc
import time
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import json
import logging
from concurrent.futures import ThreadPoolExecutor
import threading

# Import backend config (temporarily disable API config due to validation issues)
from .config import config, logger

class AdvancedGraniteModelManager:
    """Advanced IBM Granite Model Manager with API integration"""

    def __init__(self):
        self.loaded_models = {}  # Cache for multiple models
        self.current_model_key = None
        self.current_model = None
        self.current_tokenizer = None
        self.generation_pipeline = None
        self.embedding_model = None
        self.device = self._get_device()
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.model_lock = threading.Lock()

        # Model configurations - use available models from config
        self.granite_configs = config.AVAILABLE_MODELS

        logger.info(f"Advanced Granite ModelManager initialized with device: {self.device}")
        logger.info(f"Available Granite models: {list(self.granite_configs.keys())}")
    
    def _get_device(self) -> str:
        """Determine the best available device"""
        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"
    
    def _get_quantization_config(self):
        """Get quantization configuration for memory efficiency"""
        if self.device == "cuda":
            return BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
        return None
    
    def load_generation_model(self, model_key: str = None) -> bool:
        """Load a text generation model"""
        try:
            if model_key is None:
                model_key = config.DEFAULT_MODEL
            
            if self.current_model_key == model_key and self.current_model is not None:
                logger.info(f"Model {model_key} already loaded")
                return True
            
            # Clear previous model
            self._clear_current_model()
            
            model_config = config.get_model_config(model_key)
            model_id = model_config["model_id"]
            
            logger.info(f"Loading model: {model_config['name']} ({model_id})")
            
            # Load tokenizer
            self.current_tokenizer = AutoTokenizer.from_pretrained(
                model_id,
                token=config.HUGGINGFACE_TOKEN if config.HUGGINGFACE_TOKEN else None,
                trust_remote_code=True
            )
            
            # Add pad token if missing
            if self.current_tokenizer.pad_token is None:
                self.current_tokenizer.pad_token = self.current_tokenizer.eos_token
            
            # Load model with appropriate configuration
            model_kwargs = {
                "token": config.HUGGINGFACE_TOKEN if config.HUGGINGFACE_TOKEN else None,
                "trust_remote_code": True,
                "torch_dtype": torch.float16 if self.device != "cpu" else torch.float32,
                "device_map": "auto" if self.device == "cuda" else None
            }
            
            # Add quantization for CUDA
            quantization_config = self._get_quantization_config()
            if quantization_config:
                model_kwargs["quantization_config"] = quantization_config
            
            self.current_model = AutoModelForCausalLM.from_pretrained(
                model_id,
                **model_kwargs
            )
            
            # Create generation pipeline
            self.generation_pipeline = pipeline(
                "text-generation",
                model=self.current_model,
                tokenizer=self.current_tokenizer,
                device=0 if self.device == "cuda" else -1,
                torch_dtype=torch.float16 if self.device != "cpu" else torch.float32
            )
            
            self.current_model_key = model_key
            
            logger.info(f"Successfully loaded model: {model_config['name']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model {model_key}: {str(e)}")
            self._clear_current_model()
            return False
    
    def load_embedding_model(self) -> bool:
        """Load the sentence transformer model for embeddings"""
        try:
            if self.embedding_model is not None:
                logger.info("Embedding model already loaded")
                return True
            
            logger.info(f"Loading embedding model: {config.EMBEDDING_MODEL}")
            
            self.embedding_model = SentenceTransformer(
                config.EMBEDDING_MODEL,
                device=self.device
            )
            
            logger.info("Successfully loaded embedding model")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            return False
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using the current model"""
        try:
            if self.generation_pipeline is None:
                raise ValueError("No generation model loaded")
            
            # Get model configuration
            model_config = config.get_model_config(self.current_model_key)
            
            # Set generation parameters
            generation_kwargs = {
                "max_new_tokens": kwargs.get("max_new_tokens", config.MAX_NEW_TOKENS),
                "temperature": kwargs.get("temperature", model_config.get("temperature", config.TEMPERATURE)),
                "top_p": kwargs.get("top_p", config.TOP_P),
                "top_k": kwargs.get("top_k", config.TOP_K),
                "do_sample": kwargs.get("do_sample", config.DO_SAMPLE),
                "pad_token_id": self.current_tokenizer.eos_token_id,
                "return_full_text": False
            }
            
            # Generate text
            result = self.generation_pipeline(
                prompt,
                **generation_kwargs
            )
            
            if result and len(result) > 0:
                generated_text = result[0]["generated_text"]
                return generated_text.strip()
            else:
                return "I apologize, but I couldn't generate a response. Please try again."
                
        except Exception as e:
            logger.error(f"Text generation failed: {str(e)}")
            return f"Error generating response: {str(e)}"
    
    def create_embeddings(self, texts: List[str]) -> Optional[torch.Tensor]:
        """Create embeddings for a list of texts"""
        try:
            if self.embedding_model is None:
                if not self.load_embedding_model():
                    return None
            
            embeddings = self.embedding_model.encode(
                texts,
                convert_to_tensor=True,
                show_progress_bar=len(texts) > 100
            )
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Embedding creation failed: {str(e)}")
            return None
    
    def _clear_current_model(self):
        """Clear the current model from memory"""
        if self.current_model is not None:
            del self.current_model
            self.current_model = None
        
        if self.current_tokenizer is not None:
            del self.current_tokenizer
            self.current_tokenizer = None
        
        if self.generation_pipeline is not None:
            del self.generation_pipeline
            self.generation_pipeline = None
        
        self.current_model_key = None
        
        # Force garbage collection
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """Get list of available models"""
        return config.AVAILABLE_MODELS
    
    def get_current_model_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the currently loaded model"""
        if self.current_model_key:
            model_config = config.get_model_config(self.current_model_key)
            return {
                "key": self.current_model_key,
                "name": model_config["name"],
                "description": model_config["description"],
                "loaded": self.current_model is not None
            }
        return None
    
    def get_model_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage information"""
        memory_info = {
            "device": self.device,
            "model_loaded": self.current_model is not None,
            "embedding_model_loaded": self.embedding_model is not None
        }
        
        if torch.cuda.is_available():
            memory_info.update({
                "gpu_memory_allocated": torch.cuda.memory_allocated() / 1024**3,  # GB
                "gpu_memory_reserved": torch.cuda.memory_reserved() / 1024**3,    # GB
                "gpu_memory_total": torch.cuda.get_device_properties(0).total_memory / 1024**3  # GB
            })
        
        return memory_info
    
    def cleanup(self):
        """Clean up all models and free memory"""
        logger.info("Cleaning up models...")
        
        self._clear_current_model()
        
        if self.embedding_model is not None:
            del self.embedding_model
            self.embedding_model = None
        
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        logger.info("Model cleanup completed")

# Global model manager instance
model_manager = AdvancedGraniteModelManager()
