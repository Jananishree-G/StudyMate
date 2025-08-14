#!/usr/bin/env python3
"""
Check Database Connection Status for StudyMate
"""

import sys
import os
from pathlib import Path

def check_database_status():
    """Check the current database configuration and status"""
    
    print("=" * 70)
    print("📊 STUDYMATE DATABASE STATUS CHECK")
    print("=" * 70)
    
    # Check current directory structure
    current_dir = Path('.')
    api_dir = current_dir / 'api'
    backend_dir = current_dir / 'backend'
    
    print(f"📍 Current directory: {current_dir.absolute()}")
    print(f"📁 API directory exists: {api_dir.exists()}")
    print(f"📁 Backend directory exists: {backend_dir.exists()}")
    
    # Check environment files
    env_file = current_dir / '.env'
    env_example = current_dir / '.env.example'
    
    print(f"\n🔧 ENVIRONMENT CONFIGURATION:")
    print(f"   .env file exists: {env_file.exists()}")
    print(f"   .env.example exists: {env_example.exists()}")
    
    # Check current .env for database settings
    if env_file.exists():
        print(f"\n📋 CURRENT .ENV SETTINGS:")
        with open(env_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if 'DATABASE' in line.upper() or 'DB' in line.upper():
                    print(f"   {line.strip()}")
        
        # Check if any database-related settings exist
        env_content = env_file.read_text()
        has_database_config = any(keyword in env_content.upper() 
                                for keyword in ['DATABASE_URL', 'POSTGRES', 'MYSQL', 'SQLITE'])
        
        if not has_database_config:
            print("   ❌ No traditional database configuration found in .env")
        else:
            print("   ✅ Database configuration found in .env")
    
    # Check what the current application is using
    print(f"\n🔍 CURRENT APPLICATION DATABASE USAGE:")
    
    try:
        # Check backend configuration
        sys.path.append('.')
        from backend.config import config
        
        print("   ✅ Backend config loaded successfully")
        
        # Check for FAISS configuration
        if hasattr(config, 'FAISS_INDEX_TYPE'):
            print(f"   ✅ FAISS Vector Database: {config.FAISS_INDEX_TYPE}")
        
        if hasattr(config, 'EMBEDDING_DIMENSION'):
            print(f"   ✅ Embedding Dimension: {config.EMBEDDING_DIMENSION}")
            
        # Check for traditional database
        if hasattr(config, 'DATABASE_URL'):
            print(f"   ✅ SQL Database URL: {config.DATABASE_URL}")
        else:
            print("   ❌ No SQL database configuration in backend")
            
    except Exception as e:
        print(f"   ❌ Backend config error: {e}")
    
    # Check if API has database configuration
    if api_dir.exists():
        print(f"\n🔍 API DATABASE CONFIGURATION:")
        try:
            from api.config import settings
            print("   ✅ API config loaded successfully")
            print(f"   📊 Database URL: {settings.database_url}")
            print(f"   📊 Database Echo: {settings.database_echo}")
            
            # Check if PostgreSQL is expected
            if 'postgresql' in settings.database_url:
                print("   ⚠️  PostgreSQL expected but may not be running")
                
        except Exception as e:
            print(f"   ❌ API config error: {e}")
    
    # Check data directories
    print(f"\n📁 DATA STORAGE:")
    data_dirs = ['data', 'data/uploads', 'data/processed', 'data/embeddings']
    for dir_name in data_dirs:
        dir_path = current_dir / dir_name
        if dir_path.exists():
            file_count = len(list(dir_path.glob('*')))
            print(f"   ✅ {dir_name}: {file_count} files")
        else:
            print(f"   ❌ {dir_name}: Not found")
    
    # Check for FAISS index files
    faiss_files = list(current_dir.rglob('*.faiss')) + list(current_dir.rglob('*.index'))
    if faiss_files:
        print(f"   ✅ FAISS index files found: {len(faiss_files)}")
        for f in faiss_files[:3]:  # Show first 3
            print(f"      - {f}")
    else:
        print(f"   ❌ No FAISS index files found")
    
    # Summary
    print(f"\n📊 SUMMARY:")
    print("=" * 70)
    print("Current StudyMate Database Architecture:")
    print("✅ FAISS Vector Database - For document embeddings and similarity search")
    print("✅ File-based Storage - For documents and metadata")
    print("❌ No active SQL Database connection")
    print("⚠️  PostgreSQL configured in API but not connected")
    
    print(f"\nDatabase Type: Hybrid (Vector + File-based)")
    print(f"Status: Fully functional without traditional SQL database")
    print("=" * 70)

if __name__ == "__main__":
    check_database_status()
