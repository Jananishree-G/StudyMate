#!/usr/bin/env python3
"""
StudyMate Database Setup Tool
Connect and initialize PostgreSQL database for PDF storage
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_header():
    """Print setup header"""
    print("=" * 80)
    print("🗄️  STUDYMATE DATABASE SETUP TOOL")
    print("=" * 80)
    print("This tool will help you set up a PostgreSQL database for storing PDF files")
    print("and their metadata in your StudyMate project.")
    print("=" * 80)

def check_current_setup():
    """Check current database setup"""
    print("\n🔍 CHECKING CURRENT SETUP:")
    print("-" * 50)
    
    # Check .env file
    env_file = Path('.env')
    if env_file.exists():
        print("✅ .env file exists")
        
        # Read current database URL
        env_content = env_file.read_text()
        if 'DATABASE_URL' in env_content:
            for line in env_content.split('\n'):
                if line.startswith('DATABASE_URL'):
                    print(f"📊 Current: {line}")
                    return line.split('=', 1)[1] if '=' in line else None
        else:
            print("❌ No DATABASE_URL in .env file")
    else:
        print("❌ No .env file found")
    
    return None

def create_env_file():
    """Create or update .env file with database configuration"""
    print("\n🔧 DATABASE CONFIGURATION:")
    print("-" * 50)
    
    print("Choose database option:")
    print("1. PostgreSQL (Recommended for production)")
    print("2. SQLite (Simple, file-based)")
    print("3. Use existing PostgreSQL")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        return setup_postgresql()
    elif choice == '2':
        return setup_sqlite()
    elif choice == '3':
        return setup_existing_postgresql()
    else:
        print("❌ Invalid choice")
        return None

def setup_postgresql():
    """Setup new PostgreSQL database"""
    print("\n🐘 POSTGRESQL SETUP:")
    print("-" * 30)
    
    print("For PostgreSQL setup, you need:")
    print("1. PostgreSQL server installed and running")
    print("2. Database credentials")
    
    # Get database details
    host = input("Database host (default: localhost): ").strip() or "localhost"
    port = input("Database port (default: 5432): ").strip() or "5432"
    database = input("Database name (default: studymate_db): ").strip() or "studymate_db"
    username = input("Username (default: studymate): ").strip() or "studymate"
    password = input("Password (default: studymate): ").strip() or "studymate"
    
    database_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
    
    # Update .env file
    update_env_file(database_url)
    
    print(f"\n✅ PostgreSQL configuration saved!")
    print(f"📊 Database URL: {database_url}")
    
    return database_url

def setup_sqlite():
    """Setup SQLite database"""
    print("\n📁 SQLITE SETUP:")
    print("-" * 20)
    
    db_path = input("Database file path (default: ./studymate.db): ").strip() or "./studymate.db"
    database_url = f"sqlite:///{db_path}"
    
    # Update .env file
    update_env_file(database_url)
    
    print(f"\n✅ SQLite configuration saved!")
    print(f"📊 Database URL: {database_url}")
    
    return database_url

def setup_existing_postgresql():
    """Setup with existing PostgreSQL"""
    print("\n🔗 EXISTING POSTGRESQL:")
    print("-" * 25)
    
    database_url = input("Enter full DATABASE_URL: ").strip()
    
    if not database_url.startswith(('postgresql://', 'postgres://')):
        print("❌ Invalid PostgreSQL URL format")
        return None
    
    # Update .env file
    update_env_file(database_url)
    
    print(f"\n✅ PostgreSQL configuration saved!")
    print(f"📊 Database URL: {database_url}")
    
    return database_url

def update_env_file(database_url: str):
    """Update .env file with database URL"""
    env_file = Path('.env')
    
    # Read existing content
    if env_file.exists():
        lines = env_file.read_text().split('\n')
    else:
        lines = []
    
    # Update or add DATABASE_URL
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('DATABASE_URL='):
            lines[i] = f"DATABASE_URL={database_url}"
            updated = True
            break
    
    if not updated:
        lines.append(f"DATABASE_URL={database_url}")
    
    # Write back to file
    env_file.write_text('\n'.join(lines))

async def test_database_connection(database_url: str) -> bool:
    """Test database connection"""
    print("\n🔌 TESTING DATABASE CONNECTION:")
    print("-" * 35)
    
    try:
        # Add project to path
        sys.path.append('.')
        
        # Import API database components
        from api.config import Settings
        from api.database import DatabaseManager
        
        # Override settings with new database URL
        settings = Settings(database_url=database_url)
        
        # Test connection
        db_manager = DatabaseManager()
        is_connected = await db_manager.check_connection()
        
        if is_connected:
            print("✅ Database connection successful!")
            return True
        else:
            print("❌ Database connection failed!")
            return False
            
    except Exception as e:
        print(f"❌ Connection test error: {e}")
        return False

async def create_database_tables(database_url: str) -> bool:
    """Create database tables"""
    print("\n🏗️  CREATING DATABASE TABLES:")
    print("-" * 30)
    
    try:
        sys.path.append('.')
        
        from api.database import DatabaseManager
        
        # Create tables
        db_manager = DatabaseManager()
        await db_manager.create_tables()
        
        print("✅ Database tables created successfully!")
        
        # List created tables
        print("\n📋 Created tables:")
        tables = [
            "users", "documents", "document_chunks", 
            "conversations", "messages", "user_sessions",
            "model_usage", "system_metrics"
        ]
        
        for table in tables:
            print(f"   📄 {table}")
        
        return True
        
    except Exception as e:
        print(f"❌ Table creation error: {e}")
        return False

def show_usage_instructions():
    """Show how to use the database"""
    print("\n📚 HOW TO USE YOUR DATABASE:")
    print("=" * 50)
    
    print("1. 📤 UPLOAD PDF FILES:")
    print("   • Use the main StudyMate app (http://localhost:8510)")
    print("   • Or use the API endpoints")
    print("   • Files will be stored in the database with metadata")
    
    print("\n2. 🔍 ACCESS DATABASE:")
    print("   • Web interface: http://localhost:8511 (Database Browser)")
    print("   • API endpoints: http://localhost:8000/docs")
    print("   • Direct SQL access using your database client")
    
    print("\n3. 📊 DATABASE FEATURES:")
    print("   • ✅ PDF file storage and metadata")
    print("   • ✅ User management and authentication")
    print("   • ✅ Conversation history")
    print("   • ✅ Document chunks for AI processing")
    print("   • ✅ Vector embeddings storage")
    print("   • ✅ Usage tracking and analytics")
    
    print("\n4. 🚀 START USING:")
    print("   • Run: python run_api.py (for full API)")
    print("   • Or: streamlit run main.py (for basic app)")

async def main():
    """Main setup function"""
    print_header()
    
    # Check current setup
    current_db_url = check_current_setup()
    
    if current_db_url:
        print(f"\n⚠️  Database already configured: {current_db_url}")
        choice = input("Do you want to reconfigure? (y/N): ").strip().lower()
        if choice != 'y':
            print("👋 Setup cancelled")
            return
    
    # Configure database
    database_url = create_env_file()
    
    if not database_url:
        print("❌ Database configuration failed")
        return
    
    # Test connection
    connection_ok = await test_database_connection(database_url)
    
    if not connection_ok:
        print("\n⚠️  Database connection failed!")
        print("Please check:")
        print("• Database server is running")
        print("• Credentials are correct")
        print("• Network connectivity")
        return
    
    # Create tables
    tables_ok = await create_database_tables(database_url)
    
    if not tables_ok:
        print("❌ Table creation failed")
        return
    
    # Success!
    print("\n🎉 DATABASE SETUP COMPLETE!")
    print("=" * 50)
    print("✅ Database connected and configured")
    print("✅ Tables created successfully")
    print("✅ Ready to store PDF files and metadata")
    
    # Show usage instructions
    show_usage_instructions()
    
    print("\n🎯 NEXT STEPS:")
    print("1. Start the API: python run_api.py")
    print("2. Upload PDF files through the web interface")
    print("3. Access your data through the database browser")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
        import traceback
        traceback.print_exc()
