#!/usr/bin/env python3
"""
Live IBM Granite Download Monitor
Shows real-time download progress in VS Code terminal
"""

import time
import os
import sys
from pathlib import Path
import requests

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_download_status():
    """Get current download status"""
    try:
        cache_dir = Path.home() / '.cache' / 'huggingface' / 'hub'
        
        if not cache_dir.exists():
            return {"status": "no_cache", "files": [], "locks": []}
        
        incomplete_files = list(cache_dir.rglob('*.incomplete'))
        lock_files = list(cache_dir.rglob('*.lock'))
        
        file_info = []
        for file in incomplete_files:
            try:
                size_mb = file.stat().st_size / (1024*1024)
                file_info.append({
                    "name": file.name,
                    "size_mb": size_mb,
                    "path": str(file)
                })
            except:
                pass
        
        return {
            "status": "active" if incomplete_files else "complete",
            "files": file_info,
            "locks": len(lock_files),
            "total_files": len(incomplete_files)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def check_api_status():
    """Check if the API is running"""
    try:
        response = requests.get("http://localhost:8001/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "running",
                "models_loaded": data.get("models_loaded", []),
                "device": data.get("device", "unknown")
            }
    except:
        pass
    return {"status": "not_running"}

def display_status():
    """Display current status"""
    clear_screen()
    
    print("=" * 70)
    print("🚀 IBM GRANITE MODEL DOWNLOAD MONITOR")
    print("=" * 70)
    
    # Check downloads
    download_status = get_download_status()
    
    if download_status["status"] == "active":
        print(f"🔄 DOWNLOADING: {download_status['total_files']} files in progress")
        print(f"🔒 Active locks: {download_status['locks']}")
        print()
        
        print("📥 DOWNLOAD PROGRESS:")
        for i, file_info in enumerate(download_status["files"][:5]):  # Show top 5
            name = file_info["name"][:50] + "..." if len(file_info["name"]) > 50 else file_info["name"]
            size = file_info["size_mb"]
            
            # Estimate progress based on typical model sizes
            if "model-00001" in file_info["name"]:
                total_size = 4970  # ~5GB
                progress = min(100, (size / total_size) * 100)
                bar_length = 30
                filled = int(bar_length * progress / 100)
                bar = "█" * filled + "░" * (bar_length - filled)
                print(f"   📄 {name}")
                print(f"      [{bar}] {progress:.1f}% ({size:.0f}MB/{total_size}MB)")
            elif "model-00002" in file_info["name"]:
                total_size = 1990  # ~2GB
                progress = min(100, (size / total_size) * 100)
                bar_length = 30
                filled = int(bar_length * progress / 100)
                bar = "█" * filled + "░" * (bar_length - filled)
                print(f"   📄 {name}")
                print(f"      [{bar}] {progress:.1f}% ({size:.0f}MB/{total_size}MB)")
            else:
                print(f"   📄 {name}: {size:.1f} MB")
            print()
            
    elif download_status["status"] == "complete":
        print("✅ DOWNLOADS COMPLETE!")
        print("🎉 All IBM Granite model files have been downloaded")
        
    elif download_status["status"] == "no_cache":
        print("❌ No HuggingFace cache found")
        print("💡 Downloads may not have started yet")
        
    else:
        print(f"❌ Error checking downloads: {download_status.get('error', 'Unknown')}")
    
    print("-" * 70)
    
    # Check API status
    api_status = check_api_status()
    
    if api_status["status"] == "running":
        print("🌐 API STATUS: ✅ RUNNING at http://localhost:8001")
        print(f"🖥️  Device: {api_status['device']}")
        if api_status["models_loaded"]:
            print(f"🤖 Models loaded: {', '.join(api_status['models_loaded'])}")
        else:
            print("🤖 Models: ⏳ Loading in progress...")
    else:
        print("🌐 API STATUS: ❌ NOT RUNNING")
        print("💡 Start with: python real_granite_api.py")
    
    print("-" * 70)
    print("📍 DOWNLOAD LOCATION:")
    print(f"   {Path.home() / '.cache' / 'huggingface' / 'hub'}")
    print()
    print("🔄 LIVE DOWNLOAD TERMINAL: Terminal 16 (python real_granite_api.py)")
    print("📚 API Documentation: http://localhost:8001/docs")
    print("❤️  Health Check: http://localhost:8001/health")
    print()
    print("⏹️  Press Ctrl+C to stop monitoring")
    print("=" * 70)

def main():
    """Main monitoring loop"""
    try:
        while True:
            display_status()
            time.sleep(5)  # Update every 5 seconds
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped. Downloads continue in background.")
        print("🔄 Check Terminal 16 for live progress bars!")

if __name__ == "__main__":
    main()
