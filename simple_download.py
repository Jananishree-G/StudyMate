#!/usr/bin/env python3
"""
Simple IBM Granite Model Downloader
"""

import logging
import time
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def download_granite_model():
    """Download IBM Granite model"""
    logger.info("Starting IBM Granite 3B download...")
    
    try:
        from huggingface_hub import snapshot_download
        
        # Download with resume capability
        cache_dir = snapshot_download(
            repo_id="ibm-granite/granite-3b-code-instruct",
            resume_download=True,
            local_files_only=False,
            ignore_patterns=["*.bin"]  # Prefer safetensors
        )
        
        logger.info(f"Download completed! Files at: {cache_dir}")
        return True
        
    except Exception as e:
        logger.error(f"Download failed: {e}")
        
        error_str = str(e).lower()
        if "paging file" in error_str:
            logger.error("Memory issue - increase virtual memory in Windows")
        elif "connection" in error_str or "network" in error_str:
            logger.error("Network issue - check internet connection")
        elif "rate" in error_str or "429" in error_str:
            logger.error("Rate limited - wait and try again later")
        
        return False

def check_download_status():
    """Check current download status"""
    cache_dir = Path.home() / '.cache' / 'huggingface' / 'hub'
    
    if cache_dir.exists():
        incomplete_files = list(cache_dir.rglob('*.incomplete'))
        logger.info(f"Incomplete downloads: {len(incomplete_files)}")
        
        for file in incomplete_files:
            size_mb = file.stat().st_size / (1024 * 1024)
            logger.info(f"  {file.name}: {size_mb:.0f}MB")
    else:
        logger.info("No cache directory found")

def main():
    """Main function"""
    logger.info("=" * 50)
    logger.info("IBM Granite Model Downloader")
    logger.info("=" * 50)
    
    # Check current status
    logger.info("Checking current download status...")
    check_download_status()
    
    # Attempt download
    logger.info("Attempting to resume/start download...")
    success = download_granite_model()
    
    if success:
        logger.info("SUCCESS: Download completed!")
    else:
        logger.info("FAILED: Download did not complete")
    
    # Final status check
    logger.info("Final status check...")
    check_download_status()

if __name__ == "__main__":
    main()
