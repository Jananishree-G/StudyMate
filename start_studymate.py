#!/usr/bin/env python3
"""
StudyMate Startup Script
Starts both backend API and frontend application
"""

import subprocess
import time
import sys
import os
from pathlib import Path
import threading
import webbrowser

def print_banner():
    """Print startup banner"""
    print("=" * 80)
    print("🚀 STARTING STUDYMATE - AI ACADEMIC ASSISTANT")
    print("=" * 80)
    print("📚 Advanced PDF Processing with AI-Powered Q&A")
    print("🔐 User Authentication & Document Management")
    print("🤖 IBM Granite Models Integration")
    print("=" * 80)

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'streamlit', 'PyMuPDF', 
        'passlib', 'PyJWT', 'requests', 'transformers'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        for package in missing_packages:
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         capture_output=True, text=True)
        
        print("✅ Dependencies installed!")
    else:
        print("✅ All dependencies are installed!")

def start_backend():
    """Start the backend API server"""
    print("\n🔧 Starting Backend API Server...")
    
    try:
        # Start backend API
        backend_process = subprocess.Popen([
            sys.executable, "backend_api.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait a moment for startup
        time.sleep(3)
        
        # Check if process is running
        if backend_process.poll() is None:
            print("✅ Backend API started successfully on http://localhost:8000")
            return backend_process
        else:
            stdout, stderr = backend_process.communicate()
            print(f"❌ Backend failed to start:")
            print(f"   Error: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the frontend application"""
    print("\n🎨 Starting Frontend Application...")
    
    try:
        # Start Streamlit app
        frontend_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "studymate_app.py",
            "--server.port", "8501",
            "--server.headless", "true"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait a moment for startup
        time.sleep(5)
        
        # Check if process is running
        if frontend_process.poll() is None:
            print("✅ Frontend application started successfully on http://localhost:8501")
            return frontend_process
        else:
            stdout, stderr = frontend_process.communicate()
            print(f"❌ Frontend failed to start:")
            print(f"   Error: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def open_browser():
    """Open browser after delay"""
    time.sleep(8)  # Wait for both services to start
    print("\n🌐 Opening browser...")
    webbrowser.open("http://localhost:8501")

def show_status():
    """Show application status and URLs"""
    print("\n" + "=" * 80)
    print("🎉 STUDYMATE IS NOW RUNNING!")
    print("=" * 80)
    
    print("\n📊 SERVICE STATUS:")
    print("   🔧 Backend API:      http://localhost:8000")
    print("   🎨 Frontend App:     http://localhost:8501")
    print("   📖 API Docs:         http://localhost:8000/docs")
    
    print("\n🚀 GETTING STARTED:")
    print("   1. Open http://localhost:8501 in your browser")
    print("   2. Register a new account or login")
    print("   3. Upload PDF documents")
    print("   4. Chat with your documents using AI")
    
    print("\n💡 FEATURES:")
    print("   ✅ User Authentication & Registration")
    print("   ✅ PDF Upload & Processing")
    print("   ✅ AI-Powered Document Q&A")
    print("   ✅ Chat History & Document Management")
    print("   ✅ IBM Granite Models Integration")
    print("   ✅ Vector Search & Embeddings")
    
    print("\n⚠️  TO STOP:")
    print("   Press Ctrl+C to stop all services")
    print("=" * 80)

def main():
    """Main startup function"""
    print_banner()
    
    # Check dependencies
    check_dependencies()
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ Cannot start without backend API")
        return
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ Cannot start without frontend application")
        backend_process.terminate()
        return
    
    # Open browser in separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Show status
    show_status()
    
    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("❌ Backend process stopped unexpectedly")
                break
            
            if frontend_process.poll() is not None:
                print("❌ Frontend process stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down StudyMate...")
        
        # Terminate processes
        if backend_process and backend_process.poll() is None:
            backend_process.terminate()
            print("   ✅ Backend stopped")
        
        if frontend_process and frontend_process.poll() is None:
            frontend_process.terminate()
            print("   ✅ Frontend stopped")
        
        print("👋 StudyMate stopped successfully!")

if __name__ == "__main__":
    main()
