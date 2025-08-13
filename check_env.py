#!/usr/bin/env python3
"""
Quick environment checker for StudyMate
"""

import os
from pathlib import Path

def check_environment():
    """Check if environment is properly configured"""
    print("🔍 StudyMate Environment Check")
    print("=" * 40)
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("   Run: python setup_env.py")
        return False
    
    print("✅ .env file found")
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded")
    except ImportError:
        print("❌ python-dotenv not installed")
        print("   Run: pip install python-dotenv")
        return False
    
    # Check required variables
    required_vars = {
        'WATSONX_API_KEY': 'IBM Watson API Key',
        'WATSONX_PROJECT_ID': 'IBM Watson Project ID'
    }
    
    optional_vars = {
        'HUGGINGFACE_API_KEY': 'HuggingFace API Key'
    }
    
    print("\n📋 Required Variables:")
    all_good = True
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value or value.startswith('your_'):
            print(f"❌ {var}: Not configured")
            print(f"   Description: {description}")
            all_good = False
        else:
            # Show masked value
            masked = '*' * (len(value) - 4) + value[-4:] if len(value) > 4 else '*' * len(value)
            print(f"✅ {var}: {masked}")
    
    print("\n📋 Optional Variables:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if not value or value.startswith('your_'):
            print(f"⚠️  {var}: Not configured (optional)")
        else:
            masked = '*' * (len(value) - 4) + value[-4:] if len(value) > 4 else '*' * len(value)
            print(f"✅ {var}: {masked}")
    
    # Check directories
    print("\n📁 Directory Check:")
    required_dirs = ['data/uploads', 'data/processed', 'data/embeddings', 'logs']
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✅ {dir_path}: Exists")
        else:
            print(f"⚠️  {dir_path}: Will be created automatically")
    
    print("\n" + "=" * 40)
    
    if all_good:
        print("🎉 Environment is properly configured!")
        print("   You can now run: streamlit run main.py")
        return True
    else:
        print("❌ Environment setup incomplete")
        print("   Run: python setup_env.py")
        return False

if __name__ == "__main__":
    check_environment()
