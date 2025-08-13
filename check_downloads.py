#!/usr/bin/env python3
"""
Check IBM Granite Model Download Status
"""

import os
import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_huggingface_cache():
    """Check HuggingFace cache directory"""
    print("🔍 Checking HuggingFace Cache Locations...")
    
    # Common cache locations
    cache_locations = [
        Path.home() / ".cache" / "huggingface",
        Path(os.environ.get("HF_HOME", "")) if os.environ.get("HF_HOME") else None,
        Path(os.environ.get("TRANSFORMERS_CACHE", "")) if os.environ.get("TRANSFORMERS_CACHE") else None,
        Path("models") / "transformers",  # Local project cache
    ]
    
    # Remove None values
    cache_locations = [loc for loc in cache_locations if loc is not None]
    
    found_caches = []
    
    for cache_dir in cache_locations:
        if cache_dir.exists():
            print(f"✅ Found cache directory: {cache_dir}")
            found_caches.append(cache_dir)
            
            # List contents
            try:
                items = list(cache_dir.iterdir())
                print(f"   📁 Contains {len(items)} items")
                
                # Look for IBM Granite models
                for item in items:
                    if "granite" in item.name.lower() or "ibm" in item.name.lower():
                        print(f"   🤖 Found Granite-related: {item.name}")
                        
                        # Check size if it's a directory
                        if item.is_dir():
                            try:
                                size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                                size_gb = size / (1024**3)
                                print(f"      📊 Size: {size_gb:.2f} GB")
                            except:
                                print(f"      📊 Size: Unable to calculate")
                
            except PermissionError:
                print(f"   ❌ Permission denied to read {cache_dir}")
        else:
            print(f"❌ Cache directory not found: {cache_dir}")
    
    return found_caches

def check_current_downloads():
    """Check if any downloads are currently in progress"""
    print("\n🔄 Checking Current Download Status...")
    
    try:
        from transformers.utils import TRANSFORMERS_CACHE
        cache_path = Path(TRANSFORMERS_CACHE)
        
        print(f"📍 Default Transformers Cache: {cache_path}")
        
        if cache_path.exists():
            # Look for .incomplete files (partial downloads)
            incomplete_files = list(cache_path.rglob("*.incomplete"))
            if incomplete_files:
                print(f"🔄 Found {len(incomplete_files)} incomplete downloads:")
                for file in incomplete_files:
                    size = file.stat().st_size / (1024**2)  # MB
                    print(f"   📥 {file.name}: {size:.1f} MB")
            else:
                print("✅ No incomplete downloads found")
            
            # Look for lock files (active downloads)
            lock_files = list(cache_path.rglob("*.lock"))
            if lock_files:
                print(f"🔒 Found {len(lock_files)} active download locks:")
                for file in lock_files:
                    print(f"   🔒 {file.name}")
            else:
                print("✅ No active download locks found")
        
    except Exception as e:
        print(f"❌ Error checking downloads: {e}")

def check_model_availability():
    """Check which IBM Granite models are available locally"""
    print("\n🤖 Checking IBM Granite Model Availability...")
    
    granite_models = [
        "ibm-granite/granite-3b-code-instruct",
        "ibm-granite/granite-8b-code-instruct",
        "ibm-granite/granite-13b-instruct-v2"
    ]
    
    for model_id in granite_models:
        print(f"\n📋 Checking: {model_id}")
        
        try:
            from transformers import AutoTokenizer
            
            # Try to load tokenizer (lightweight check)
            tokenizer = AutoTokenizer.from_pretrained(
                model_id,
                trust_remote_code=True,
                local_files_only=True  # Only check local files
            )
            print(f"   ✅ Tokenizer available locally")
            
            # Try to check model files
            from transformers import AutoModelForCausalLM
            try:
                # Just check if model files exist locally
                model = AutoModelForCausalLM.from_pretrained(
                    model_id,
                    trust_remote_code=True,
                    local_files_only=True,
                    torch_dtype="auto"
                )
                print(f"   ✅ Model files available locally")
                
                # Get model size estimate
                param_count = sum(p.numel() for p in model.parameters())
                size_gb = param_count * 4 / (1024**3)  # Rough estimate (4 bytes per param)
                print(f"   📊 Estimated size: {size_gb:.1f} GB")
                
                del model  # Free memory
                
            except Exception as e:
                print(f"   ❌ Model files not available locally: {e}")
                
        except Exception as e:
            print(f"   ❌ Not available locally: {e}")

def main():
    """Main function"""
    print("""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                                                                              ║
    ║   🔍 IBM Granite Model Download Status Checker                              ║
    ║                                                                              ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Check cache directories
    found_caches = check_huggingface_cache()
    
    # Check current downloads
    check_current_downloads()
    
    # Check model availability
    check_model_availability()
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    
    if found_caches:
        print(f"✅ Found {len(found_caches)} cache directories")
        for cache in found_caches:
            print(f"   📁 {cache}")
    else:
        print("❌ No HuggingFace cache directories found")
    
    print("\n💡 TIPS:")
    print("• Models download to: ~/.cache/huggingface/hub/")
    print("• Large models (7GB+) take time to download")
    print("• Check your internet connection if downloads are slow")
    print("• Downloads resume automatically if interrupted")

if __name__ == "__main__":
    main()
