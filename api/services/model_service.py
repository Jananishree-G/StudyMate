"""
IBM Granite Model Service for StudyMate API
Advanced model management with HuggingFace integration
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from concurrent.futures import ThreadPoolExecutor
import threading
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    GenerationConfig,
    BitsAndBytesConfig
)
from sentence_transformers import SentenceTransformer
import gc

from ..config import settings

logger = logging.getLogger(__name__)

class GraniteModelService:
    """Advanced IBM Granite model service"""
    
    def __init__(self):
        self.loaded_models: Dict[str, Dict[str, Any]] = {}
        self.current_model_key: Optional[str] = None
        self.embedding_model: Optional[SentenceTransformer] = None
        self.device = self._get_device()
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="model")
        self.model_lock = threading.Lock()
        self.generation_lock = threading.Lock()
        
        logger.info(f"Granite Model Service initialized with device: {self.device}")
    
    def _get_device(self) -> str:
        """Determine the best available device"""
        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"
    
    def _get_quantization_config(self) -> Optional[BitsAndBytesConfig]:
        """Get quantization configuration for memory efficiency"""
        if self.device == "cuda":
            return BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
        return None
    
    async def initialize(self):
        """Initialize the model service"""
        logger.info("Initializing Granite Model Service...")
        
        # Load embedding model first (required for vector operations)
        await self.load_embedding_model()
        
        # Load default Granite model
        default_model = settings.default_granite_model
        await self.load_granite_model(default_model)
        
        logger.info("Granite Model Service initialization complete")
    
    async def load_embedding_model(self) -> bool:
        """Load the sentence transformer model for embeddings"""
        try:
            if self.embedding_model is not None:
                logger.info("Embedding model already loaded")
                return True
            
            logger.info(f"Loading embedding model: {settings.embedding_model}")
            
            # Load in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            self.embedding_model = await loop.run_in_executor(
                self.executor,
                lambda: SentenceTransformer(
                    settings.embedding_model,
                    device=self.device,
                    cache_folder=str(settings.models_dir / "sentence_transformers")
                )
            )
            
            logger.info("Embedding model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            return False
    
    async def load_granite_model(self, model_key: str) -> bool:
        """Load a specific IBM Granite model"""
        try:
            if model_key in self.loaded_models:
                logger.info(f"Granite model {model_key} already loaded")
                self.current_model_key = model_key
                return True
            
            model_config = settings.granite_models.get(model_key)
            if not model_config:
                logger.error(f"Unknown Granite model: {model_key}")
                return False
            
            model_id = model_config["model_id"]
            logger.info(f"Loading Granite model: {model_config['name']} ({model_id})")
            
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
                max_new_tokens=model_config.get("max_length", 2048),
                temperature=model_config.get("temperature", 0.7),
                top_p=model_config.get("top_p", 0.9),
                top_k=model_config.get("top_k", 50),
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
            
            logger.info(f"Successfully loaded Granite model: {model_config['name']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load Granite model {model_key}: {e}")
            return False
    
    def _load_tokenizer(self, model_id: str) -> AutoTokenizer:
        """Load tokenizer in thread pool"""
        tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            token=settings.huggingface_token,
            trust_remote_code=True,
            cache_dir=str(settings.models_dir / "transformers")
        )
        
        # Add pad token if missing
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        return tokenizer
    
    def _load_model(self, model_id: str) -> AutoModelForCausalLM:
        """Load model in thread pool"""
        model_kwargs = {
            "token": settings.huggingface_token,
            "trust_remote_code": True,
            "torch_dtype": torch.float16 if self.device != "cpu" else torch.float32,
            "device_map": "auto" if self.device == "cuda" else None,
            "cache_dir": str(settings.models_dir / "transformers")
        }
        
        # Add quantization for CUDA
        quantization_config = self._get_quantization_config()
        if quantization_config:
            model_kwargs["quantization_config"] = quantization_config
        
        model = AutoModelForCausalLM.from_pretrained(model_id, **model_kwargs)
        
        # Move to device if not using device_map
        if model_kwargs["device_map"] is None and self.device != "cpu":
            model = model.to(self.device)
        
        return model
    
    async def generate_text(
        self,
        prompt: str,
        model_key: Optional[str] = None,
        **generation_kwargs
    ) -> str:
        """Generate text using IBM Granite model"""
        try:
            # Use current model if not specified
            if model_key is None:
                model_key = self.current_model_key
            
            if model_key not in self.loaded_models:
                logger.error(f"Model {model_key} not loaded")
                return "Error: Model not available"
            
            model_data = self.loaded_models[model_key]
            model = model_data["model"]
            tokenizer = model_data["tokenizer"]
            base_config = model_data["generation_config"]
            
            # Merge generation parameters
            generation_config = GenerationConfig(
                **base_config.to_dict(),
                **generation_kwargs
            )
            
            # Generate in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            
            with self.generation_lock:
                generated_text = await loop.run_in_executor(
                    self.executor,
                    self._generate_text_sync,
                    model,
                    tokenizer,
                    prompt,
                    generation_config
                )
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            return f"Error generating response: {str(e)}"
    
    def _generate_text_sync(
        self,
        model: AutoModelForCausalLM,
        tokenizer: AutoTokenizer,
        prompt: str,
        generation_config: GenerationConfig
    ) -> str:
        """Synchronous text generation"""
        try:
            # Tokenize input
            inputs = tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=2048
            )
            
            # Move to device
            if self.device != "cpu":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    generation_config=generation_config,
                    return_dict_in_generate=True,
                    output_scores=True
                )
            
            # Decode output
            generated_ids = outputs.sequences[0][inputs["input_ids"].shape[1]:]
            generated_text = tokenizer.decode(generated_ids, skip_special_tokens=True)
            
            return generated_text.strip()
            
        except Exception as e:
            logger.error(f"Synchronous generation failed: {e}")
            return f"Generation error: {str(e)}"
    
    async def create_embeddings(self, texts: List[str]) -> Optional[torch.Tensor]:
        """Create embeddings for texts"""
        try:
            if self.embedding_model is None:
                logger.error("Embedding model not loaded")
                return None
            
            # Generate embeddings in thread pool
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                self.executor,
                lambda: self.embedding_model.encode(
                    texts,
                    convert_to_tensor=True,
                    show_progress_bar=len(texts) > 100
                )
            )
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Embedding creation failed: {e}")
            return None
    
    async def switch_model(self, model_key: str) -> bool:
        """Switch to a different Granite model"""
        if model_key not in settings.granite_models:
            logger.error(f"Unknown model: {model_key}")
            return False
        
        if model_key not in self.loaded_models:
            success = await self.load_granite_model(model_key)
            if not success:
                return False
        
        self.current_model_key = model_key
        logger.info(f"Switched to model: {model_key}")
        return True
    
    async def get_loaded_models(self) -> List[str]:
        """Get list of loaded models"""
        return list(self.loaded_models.keys())
    
    async def get_current_model_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the current model"""
        if self.current_model_key and self.current_model_key in self.loaded_models:
            model_data = self.loaded_models[self.current_model_key]
            config = model_data["config"]
            
            return {
                "key": self.current_model_key,
                "name": config["name"],
                "description": config["description"],
                "model_id": config["model_id"],
                "loaded_at": model_data["loaded_at"],
                "parameters": {
                    "max_length": config.get("max_length", 2048),
                    "temperature": config.get("temperature", 0.7),
                    "top_p": config.get("top_p", 0.9),
                    "top_k": config.get("top_k", 50)
                }
            }
        return None
    
    async def get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage information"""
        memory_info = {
            "device": self.device,
            "loaded_models": len(self.loaded_models),
            "embedding_model_loaded": self.embedding_model is not None
        }
        
        if torch.cuda.is_available():
            memory_info.update({
                "gpu_memory_allocated": torch.cuda.memory_allocated() / 1024**3,  # GB
                "gpu_memory_reserved": torch.cuda.memory_reserved() / 1024**3,    # GB
                "gpu_memory_total": torch.cuda.get_device_properties(0).total_memory / 1024**3  # GB
            })
        
        return memory_info
    
    async def cleanup(self):
        """Clean up models and free memory"""
        logger.info("Cleaning up Granite models...")
        
        with self.model_lock:
            # Clear loaded models
            for model_key in list(self.loaded_models.keys()):
                model_data = self.loaded_models[model_key]
                del model_data["model"]
                del model_data["tokenizer"]
            
            self.loaded_models.clear()
            self.current_model_key = None
            
            # Clear embedding model
            if self.embedding_model is not None:
                del self.embedding_model
                self.embedding_model = None
        
        # Force garbage collection
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("Model cleanup completed")

# Global model service instance
model_service = GraniteModelService()
