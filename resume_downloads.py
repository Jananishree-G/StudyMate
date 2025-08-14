#!/usr/bin/env python3
"""
Resume IBM Granite Model Downloads
Dedicated script to resume and monitor downloads
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import List, Dict, Any
import gc

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_memory():
    """Check available memory"""
    try:
        import psutil
        memory = psutil.virtual_memory()
        logger.info(f"Memory: {memory.percent}% used, {memory.available / 1024**3:.1f}GB available")
        return memory.available > 4 * 1024**3  # Need at least 4GB
    except ImportError:
        logger.warning("psutil not available, cannot check memory")
        return True

def increase_virtual_memory():
    """Suggest increasing virtual memory"""
    logger.info("💡 To fix memory issues:")
    logger.info("1. Open System Properties > Advanced > Performance Settings")
    logger.info("2. Go to Advanced tab > Virtual Memory > Change")
    logger.info("3. Set custom size: Initial 8192 MB, Maximum 16384 MB")
    logger.info("4. Restart the download process")

def resume_granite_download(model_id: str, max_retries: int = 3):
    """Resume downloading a specific IBM Granite model"""
    logger.info(f"🔄 Resuming download for: {model_id}")
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1}/{max_retries}")
            
            # Import here to avoid memory issues
            from transformers import AutoTokenizer
            
            # First, ensure tokenizer is downloaded
            logger.info("📥 Downloading tokenizer...")
            tokenizer = AutoTokenizer.from_pretrained(
                model_id,
                trust_remote_code=True,
                resume_download=True
            )
            logger.info("✅ Tokenizer downloaded successfully")
            
            # Clear memory
            del tokenizer
            gc.collect()
            
            # Now try to download model files (without loading into memory)
            logger.info("📥 Downloading model files...")
            from huggingface_hub import snapshot_download
            
            # Download model files to cache
            cache_dir = snapshot_download(
                repo_id=model_id,
                resume_download=True,
                local_files_only=False,
                ignore_patterns=["*.bin"]  # Prefer safetensors
            )
            
            logger.info(f"✅ Model files downloaded to: {cache_dir}")
            return True
            
        except Exception as e:
            error_msg = str(e).lower()
            
            if "paging file" in error_msg or "memory" in error_msg:
                logger.error(f"❌ Memory error on attempt {attempt + 1}: {e}")
                if attempt == 0:
                    increase_virtual_memory()
                
                # Try to free memory
                gc.collect()
                time.sleep(5)
                
            elif "connection" in error_msg or "network" in error_msg:
                logger.error(f"❌ Network error on attempt {attempt + 1}: {e}")
                logger.info("⏳ Waiting 10 seconds before retry...")
                time.sleep(10)
                
            elif "rate" in error_msg or "429" in error_msg:
                logger.error(f"❌ Rate limited on attempt {attempt + 1}: {e}")
                wait_time = 60 * (attempt + 1)  # Exponential backoff
                logger.info(f"⏳ Waiting {wait_time} seconds due to rate limiting...")
                time.sleep(wait_time)
                
            else:
                logger.error(f"❌ Unknown error on attempt {attempt + 1}: {e}")
                time.sleep(5)
    
    logger.error(f"❌ Failed to download {model_id} after {max_retries} attempts")
    return False

def monitor_download_progress():
    """Monitor download progress"""
    cache_dir = Path.home() / '.cache' / 'huggingface' / 'hub'
    
    if not cache_dir.exists():
        logger.error("❌ HuggingFace cache directory not found")
        return
    
    logger.info(f"📍 Monitoring cache directory: {cache_dir}")
    
    # Get initial file sizes
    incomplete_files = list(cache_dir.rglob('*.incomplete'))
    initial_sizes = {}
    
    for file in incomplete_files:
        initial_sizes[file.name] = file.stat().st_size
    
    logger.info(f"📥 Found {len(incomplete_files)} incomplete downloads")
    
    # Monitor for 60 seconds
    for i in range(12):  # 12 * 5 seconds = 60 seconds
        time.sleep(5)
        
        current_incomplete = list(cache_dir.rglob('*.incomplete'))
        active_downloads = 0
        
        for file in current_incomplete:
            if file.name in initial_sizes:
                current_size = file.stat().st_size
                initial_size = initial_sizes[file.name]
                
                if current_size > initial_size:
                    growth = (current_size - initial_size) / (1024 * 1024)
                    logger.info(f"📈 {file.name[:20]}...: +{growth:.1f}MB")
                    active_downloads += 1
                    initial_sizes[file.name] = current_size
        
        if active_downloads > 0:
            logger.info(f"🔄 {active_downloads} files actively downloading...")
        else:
            logger.info("⏸️ No active downloads detected")
    
    # Final status
    final_incomplete = list(cache_dir.rglob('*.incomplete'))
    logger.info(f"📊 Final status: {len(final_incomplete)} incomplete files remaining")

def main():
    """Main function to resume downloads"""
    print("""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                                                                              ║
    ║   🔄 IBM Granite Model Download Resumer                                     ║
    ║                                                                              ║
    ║   Resuming interrupted downloads from HuggingFace                           ║
    ║                                                                              ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Check system resources
    if not check_memory():
        logger.warning("⚠️ Low memory detected - downloads may fail")
        increase_virtual_memory()
    
    # IBM Granite models to download
    models_to_download = [
        "ibm-granite/granite-3b-code-instruct",
        # "ibm-granite/granite-8b-code-instruct",  # Comment out for now due to memory
    ]
    
    success_count = 0
    
    for model_id in models_to_download:
        logger.info(f"\n{'='*60}")
        logger.info(f"🚀 Starting download: {model_id}")
        logger.info(f"{'='*60}")
        
        if resume_granite_download(model_id):
            success_count += 1
            logger.info(f"✅ Successfully downloaded: {model_id}")
        else:
            logger.error(f"❌ Failed to download: {model_id}")
        
        # Monitor progress
        logger.info("📊 Monitoring download progress...")
        monitor_download_progress()
        
        # Brief pause between models
        time.sleep(10)
    
    # Final summary
    logger.info(f"\n{'='*60}")
    logger.info("📊 DOWNLOAD SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"✅ Successful downloads: {success_count}/{len(models_to_download)}")
    
    if success_count == len(models_to_download):
        logger.info("🎉 All downloads completed successfully!")
    else:
        logger.warning("⚠️ Some downloads failed - check logs above")
    
    # Check final status
    cache_dir = Path.home() / '.cache' / 'huggingface' / 'hub'
    if cache_dir.exists():
        incomplete_files = list(cache_dir.rglob('*.incomplete'))
        logger.info(f"📥 Remaining incomplete files: {len(incomplete_files)}")
        
        if incomplete_files:
            total_size = sum(f.stat().st_size for f in incomplete_files) / (1024**3)
            logger.info(f"📊 Total incomplete data: {total_size:.1f}GB")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n👋 Download process interrupted by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
