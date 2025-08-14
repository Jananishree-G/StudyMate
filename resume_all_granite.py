#!/usr/bin/env python3
"""
Resume All IBM Granite Model Downloads
Shows live progress in VS Code terminal
"""

import time
import logging
from pathlib import Path
from typing import List, Dict

# Configure logging for terminal display
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def print_header():
    """Print header for download resumption"""
    print("=" * 80)
    print("🚀 RESUMING ALL IBM GRANITE MODEL DOWNLOADS")
    print("=" * 80)
    print("📍 Location: VS Code Terminal Window")
    print("🕒 Started:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)

def check_download_status():
    """Check current download status"""
    cache_dir = Path.home() / '.cache' / 'huggingface' / 'hub'
    
    print("\n🔍 CHECKING CURRENT STATUS:")
    print("-" * 50)
    
    if not cache_dir.exists():
        print("❌ HuggingFace cache directory not found")
        return []
    
    incomplete_files = list(cache_dir.rglob('*.incomplete'))
    lock_files = list(cache_dir.rglob('*.lock'))
    
    print(f"📥 Incomplete downloads: {len(incomplete_files)}")
    print(f"🔒 Active locks: {len(lock_files)}")
    
    if incomplete_files:
        total_incomplete_size = 0
        for file in incomplete_files:
            size_mb = file.stat().st_size / (1024 * 1024)
            total_incomplete_size += size_mb
            print(f"   📄 {file.name[:50]}... : {size_mb:>8.1f} MB")
        
        print(f"📊 Total incomplete: {total_incomplete_size:>8.1f} MB ({total_incomplete_size/1024:.2f} GB)")
    
    return incomplete_files

def download_granite_model(model_id: str, model_name: str) -> bool:
    """Download a specific IBM Granite model with progress display"""
    print(f"\n🚀 STARTING DOWNLOAD: {model_name}")
    print("=" * 60)
    print(f"📋 Model ID: {model_id}")
    
    try:
        from huggingface_hub import snapshot_download
        
        print("📥 Initiating download...")
        
        # Download with progress
        cache_dir = snapshot_download(
            repo_id=model_id,
            resume_download=True,
            local_files_only=False
        )
        
        print(f"✅ SUCCESS: {model_name} downloaded!")
        print(f"📁 Location: {cache_dir}")
        return True
        
    except Exception as e:
        error_msg = str(e).lower()
        print(f"❌ FAILED: {model_name}")
        print(f"🔍 Error: {e}")
        
        if "rate" in error_msg or "429" in error_msg:
            print("⏳ Rate limited - will retry later")
        elif "connection" in error_msg or "network" in error_msg:
            print("🌐 Network issue - check internet connection")
        elif "paging file" in error_msg or "memory" in error_msg:
            print("💾 Memory issue - increase virtual memory")
        elif "not found" in error_msg or "404" in error_msg:
            print("🔍 Model not found or access restricted")
        
        return False

def monitor_progress(duration_seconds: int = 30):
    """Monitor download progress for specified duration"""
    print(f"\n📊 MONITORING PROGRESS FOR {duration_seconds} SECONDS:")
    print("-" * 50)
    
    cache_dir = Path.home() / '.cache' / 'huggingface' / 'hub'
    
    if not cache_dir.exists():
        print("❌ Cache directory not found")
        return
    
    # Get initial sizes
    incomplete_files = list(cache_dir.rglob('*.incomplete'))
    initial_sizes = {}
    
    for file in incomplete_files:
        initial_sizes[file.name] = file.stat().st_size
    
    print(f"📥 Monitoring {len(incomplete_files)} incomplete files...")
    
    # Monitor for specified duration
    intervals = duration_seconds // 5  # Check every 5 seconds
    
    for i in range(intervals):
        time.sleep(5)
        
        current_incomplete = list(cache_dir.rglob('*.incomplete'))
        active_downloads = 0
        total_growth = 0
        
        print(f"\n⏰ Check {i+1}/{intervals} ({(i+1)*5}s elapsed):")
        
        for file in current_incomplete:
            if file.name in initial_sizes:
                current_size = file.stat().st_size
                initial_size = initial_sizes[file.name]
                
                if current_size > initial_size:
                    growth_mb = (current_size - initial_size) / (1024 * 1024)
                    total_growth += growth_mb
                    print(f"   📈 {file.name[:30]}... : +{growth_mb:>6.1f} MB")
                    active_downloads += 1
                    initial_sizes[file.name] = current_size
                else:
                    current_mb = current_size / (1024 * 1024)
                    print(f"   ⏸️  {file.name[:30]}... : {current_mb:>6.1f} MB (no change)")
        
        if active_downloads > 0:
            print(f"   🔄 {active_downloads} files downloading, +{total_growth:.1f} MB total")
        else:
            print(f"   ⏸️  No active downloads detected")

def main():
    """Main function to resume all IBM Granite downloads"""
    print_header()
    
    # IBM Granite models to download
    granite_models = [
        {
            "id": "ibm-granite/granite-3b-code-instruct",
            "name": "IBM Granite 3B Code Instruct",
            "priority": 1
        },
        {
            "id": "ibm-granite/granite-8b-code-instruct", 
            "name": "IBM Granite 8B Code Instruct",
            "priority": 2
        },
        {
            "id": "ibm-granite/granite-13b-instruct-v2",
            "name": "IBM Granite 13B Instruct V2",
            "priority": 3
        }
    ]
    
    # Check initial status
    initial_incomplete = check_download_status()
    
    print(f"\n🎯 DOWNLOAD PLAN:")
    print("-" * 50)
    for i, model in enumerate(granite_models, 1):
        print(f"{i}. {model['name']}")
        print(f"   📋 {model['id']}")
    
    # Start downloads
    successful_downloads = 0
    
    for model in granite_models:
        print(f"\n{'='*80}")
        
        if download_granite_model(model["id"], model["name"]):
            successful_downloads += 1
            
            # Monitor progress after each successful initiation
            print(f"\n📊 Monitoring {model['name']} progress...")
            monitor_progress(30)  # Monitor for 30 seconds
        else:
            print(f"⚠️  Skipping to next model due to error")
        
        # Brief pause between models
        time.sleep(5)
    
    # Final status check
    print(f"\n{'='*80}")
    print("📊 FINAL DOWNLOAD STATUS")
    print("=" * 80)
    
    final_incomplete = check_download_status()
    
    print(f"\n📈 SUMMARY:")
    print(f"   🚀 Models attempted: {len(granite_models)}")
    print(f"   ✅ Successful initiations: {successful_downloads}")
    print(f"   📥 Initial incomplete files: {len(initial_incomplete)}")
    print(f"   📥 Final incomplete files: {len(final_incomplete)}")
    
    if len(final_incomplete) < len(initial_incomplete):
        print(f"   🎉 Progress made: {len(initial_incomplete) - len(final_incomplete)} files completed!")
    elif len(final_incomplete) == 0:
        print(f"   🎉 ALL DOWNLOADS COMPLETE!")
    else:
        print(f"   🔄 Downloads in progress...")
    
    print(f"\n🕒 Completed: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Keep monitoring if downloads are active
    if final_incomplete:
        print("\n🔄 CONTINUING TO MONITOR ACTIVE DOWNLOADS...")
        print("Press Ctrl+C to stop monitoring")
        
        try:
            while True:
                monitor_progress(60)  # Monitor every minute
                
                # Check if downloads completed
                current_incomplete = list(Path.home().rglob('*.incomplete'))
                if not current_incomplete:
                    print("\n🎉 ALL DOWNLOADS COMPLETED!")
                    break
                    
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped by user")
            print("Downloads will continue in background")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Download process interrupted by user")
        print("Downloads may continue in background")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
