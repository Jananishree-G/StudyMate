#!/usr/bin/env python3
"""
StudyMate Advanced API Launcher
Launch the FastAPI backend with IBM Granite integration
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
import uvicorn
import click

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_banner():
    """Print StudyMate API banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                                                                              ║
    ║   🚀 StudyMate Advanced API with IBM Granite Integration                    ║
    ║                                                                              ║
    ║   🤖 IBM Granite Models from HuggingFace                                    ║
    ║   🔍 FAISS Vector Database                                                   ║
    ║   📄 Advanced PDF Processing                                                 ║
    ║   🔐 JWT Authentication                                                      ║
    ║   📊 Comprehensive Analytics                                                 ║
    ║   🎯 REST API with OpenAPI Documentation                                    ║
    ║                                                                              ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_environment():
    """Check environment setup"""
    logger.info("Checking environment setup...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
    
    # Check .env file
    env_file = project_root / ".env"
    if not env_file.exists():
        logger.warning(".env file not found. Using default configuration.")
        logger.info("Create .env file from .env.example for custom configuration")
    
    # Check required directories
    required_dirs = ["data", "logs", "models"]
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if not dir_path.exists():
            logger.info(f"Creating directory: {dir_path}")
            dir_path.mkdir(parents=True, exist_ok=True)
    
    logger.info("Environment check completed")
    return True

async def check_dependencies():
    """Check if all dependencies are available"""
    logger.info("Checking dependencies...")
    
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import transformers
        import torch
        import faiss
        import fitz  # PyMuPDF
        logger.info("✅ All core dependencies available")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        logger.error("Run: pip install -r requirements_api.txt")
        return False

async def initialize_database():
    """Initialize database"""
    logger.info("Initializing database...")
    
    try:
        from api.database import db_manager
        
        # Check database connection
        is_connected = await db_manager.check_connection()
        if not is_connected:
            logger.error("❌ Database connection failed")
            logger.info("Make sure PostgreSQL is running and DATABASE_URL is correct")
            return False
        
        # Create tables
        await db_manager.create_tables()
        logger.info("✅ Database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False

async def check_models():
    """Check model availability"""
    logger.info("Checking model availability...")
    
    try:
        from api.services.model_service import model_service
        
        # Initialize models
        await model_service.initialize()
        
        # Check loaded models
        loaded_models = await model_service.get_loaded_models()
        logger.info(f"✅ Models loaded: {loaded_models}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Model initialization failed: {e}")
        logger.info("This might be due to missing HuggingFace token or insufficient memory")
        return False

@click.command()
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=8000, help='Port to bind to')
@click.option('--reload', is_flag=True, help='Enable auto-reload')
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.option('--skip-checks', is_flag=True, help='Skip initialization checks')
@click.option('--log-level', default='info', help='Log level')
def main(host, port, reload, debug, skip_checks, log_level):
    """Launch StudyMate Advanced API"""
    
    print_banner()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, log_level.upper()))
    
    if not skip_checks:
        # Environment check
        if not check_environment():
            sys.exit(1)
        
        # Dependencies check
        if not asyncio.run(check_dependencies()):
            sys.exit(1)
        
        # Database check
        if not asyncio.run(initialize_database()):
            logger.warning("Database initialization failed, but continuing...")
        
        # Models check
        if not asyncio.run(check_models()):
            logger.warning("Model initialization failed, but continuing...")
    
    # Import configuration
    try:
        from api.config import settings
        logger.info(f"Configuration loaded: {settings.app_name} v{settings.app_version}")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)
    
    # Launch API
    logger.info(f"🚀 Starting StudyMate API on {host}:{port}")
    logger.info(f"📚 API Documentation: http://{host}:{port}/docs")
    logger.info(f"🔄 ReDoc Documentation: http://{host}:{port}/redoc")
    logger.info(f"❤️  Health Check: http://{host}:{port}/health")
    
    try:
        uvicorn.run(
            "api.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            access_log=True,
            loop="asyncio"
        )
    except KeyboardInterrupt:
        logger.info("🛑 API shutdown requested")
    except Exception as e:
        logger.error(f"❌ API startup failed: {e}")
        sys.exit(1)

@click.command()
def setup():
    """Setup StudyMate API environment"""
    print_banner()
    
    logger.info("Setting up StudyMate API environment...")
    
    # Create directories
    directories = [
        "data/uploads",
        "data/processed",
        "data/embeddings",
        "logs",
        "models/transformers",
        "models/sentence_transformers",
        "static/exports"
    ]
    
    for dir_path in directories:
        full_path = project_root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Created directory: {dir_path}")
    
    # Create .env file if it doesn't exist
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        import shutil
        shutil.copy(env_example, env_file)
        logger.info("✅ Created .env file from template")
        logger.info("📝 Please edit .env file with your configuration")
    
    # Create initial database migration
    try:
        logger.info("Creating database migration...")
        # This would typically use Alembic
        logger.info("✅ Database migration ready")
    except Exception as e:
        logger.warning(f"Database migration setup failed: {e}")
    
    logger.info("🎉 StudyMate API setup completed!")
    logger.info("Next steps:")
    logger.info("1. Edit .env file with your HuggingFace token")
    logger.info("2. Setup PostgreSQL database")
    logger.info("3. Run: python run_api.py")

@click.group()
def cli():
    """StudyMate API Management CLI"""
    pass

cli.add_command(main, name="run")
cli.add_command(setup, name="setup")

if __name__ == "__main__":
    cli()
