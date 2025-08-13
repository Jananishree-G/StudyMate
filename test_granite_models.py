#!/usr/bin/env python3
"""
Test IBM Granite Models from HuggingFace
Check if models can be loaded and used properly
"""

import os
import sys
import logging
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test if all required packages are available"""
    logger.info("Testing imports...")
    
    try:
        import torch
        logger.info(f"✅ PyTorch: {torch.__version__}")
        
        import transformers
        logger.info(f"✅ Transformers: {transformers.__version__}")
        
        from transformers import AutoTokenizer, AutoModelForCausalLM
        logger.info("✅ AutoTokenizer and AutoModelForCausalLM imported")
        
        import sentence_transformers
        logger.info(f"✅ Sentence Transformers: {sentence_transformers.__version__}")
        
        import faiss
        logger.info(f"✅ FAISS: {faiss.__version__}")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        return False

def check_device():
    """Check available compute devices"""
    logger.info("Checking compute devices...")
    
    import torch
    
    if torch.cuda.is_available():
        logger.info(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
        logger.info(f"   GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        return "cuda"
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        logger.info("✅ MPS (Apple Silicon) available")
        return "mps"
    else:
        logger.info("✅ CPU only")
        return "cpu"

def test_huggingface_connection():
    """Test HuggingFace Hub connection"""
    logger.info("Testing HuggingFace connection...")
    
    try:
        from huggingface_hub import HfApi
        
        api = HfApi()
        
        # Test connection by getting model info
        granite_models = [
            "ibm-granite/granite-3b-code-instruct",
            "ibm-granite/granite-8b-code-instruct", 
            "ibm-granite/granite-13b-instruct-v2"
        ]
        
        available_models = []
        
        for model_id in granite_models:
            try:
                model_info = api.model_info(model_id)
                logger.info(f"✅ Found model: {model_id}")
                available_models.append(model_id)
            except Exception as e:
                logger.warning(f"⚠️  Model not accessible: {model_id} - {e}")
        
        return available_models
        
    except Exception as e:
        logger.error(f"❌ HuggingFace connection failed: {e}")
        return []

def test_load_granite_model(model_id: str, device: str = "cpu"):
    """Test loading a specific IBM Granite model"""
    logger.info(f"Testing model loading: {model_id}")
    
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        # Load tokenizer
        logger.info("Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            trust_remote_code=True
        )
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        logger.info("✅ Tokenizer loaded successfully")
        
        # Load model (with reduced precision for testing)
        logger.info("Loading model...")
        
        model_kwargs = {
            "trust_remote_code": True,
            "torch_dtype": torch.float16 if device != "cpu" else torch.float32,
            "device_map": "auto" if device == "cuda" else None
        }
        
        # For CPU testing, use smaller model or skip
        if device == "cpu" and "13b" in model_id.lower():
            logger.warning("⚠️  Skipping 13B model on CPU (too large)")
            return False
        
        model = AutoModelForCausalLM.from_pretrained(model_id, **model_kwargs)
        
        if device != "cpu" and model_kwargs["device_map"] is None:
            model = model.to(device)
        
        logger.info("✅ Model loaded successfully")
        
        # Test generation
        logger.info("Testing text generation...")
        
        test_prompt = "Explain what machine learning is:"
        inputs = tokenizer(test_prompt, return_tensors="pt")
        
        if device != "cpu":
            inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=50,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        logger.info(f"✅ Generated text: {generated_text[:100]}...")
        
        # Cleanup
        del model
        del tokenizer
        
        if device == "cuda":
            torch.cuda.empty_cache()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Model loading failed: {e}")
        return False

def test_embedding_model():
    """Test sentence transformer model for embeddings"""
    logger.info("Testing embedding model...")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # Test embedding generation
        texts = ["This is a test sentence.", "Another test sentence."]
        embeddings = model.encode(texts)
        
        logger.info(f"✅ Embeddings shape: {embeddings.shape}")
        logger.info(f"✅ Embedding dimension: {embeddings.shape[1]}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Embedding model failed: {e}")
        return False

def main():
    """Main test function"""
    print("""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                                                                              ║
    ║   🧪 IBM Granite Models Test Suite                                          ║
    ║                                                                              ║
    ║   Testing HuggingFace integration and model loading                         ║
    ║                                                                              ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Test 1: Check imports
    if not test_imports():
        logger.error("❌ Import test failed. Install missing packages.")
        return False
    
    # Test 2: Check device
    device = check_device()
    
    # Test 3: Test HuggingFace connection
    available_models = test_huggingface_connection()
    
    if not available_models:
        logger.error("❌ No IBM Granite models accessible")
        return False
    
    # Test 4: Test embedding model
    if not test_embedding_model():
        logger.error("❌ Embedding model test failed")
        return False
    
    # Test 5: Test loading IBM Granite models
    success_count = 0
    
    for model_id in available_models[:1]:  # Test only first model to save time
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing model: {model_id}")
        logger.info(f"{'='*60}")
        
        if test_load_granite_model(model_id, device):
            success_count += 1
        
        time.sleep(2)  # Brief pause between tests
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"✅ Available models: {len(available_models)}")
    logger.info(f"✅ Successfully tested: {success_count}")
    logger.info(f"✅ Device: {device}")
    
    if success_count > 0:
        logger.info("🎉 IBM Granite models are working!")
        return True
    else:
        logger.error("❌ No models could be loaded successfully")
        return False

if __name__ == "__main__":
    import torch
    success = main()
    sys.exit(0 if success else 1)
