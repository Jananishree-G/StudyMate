"""
Database configuration and session management for StudyMate API
"""

import logging
from typing import AsyncGenerator
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .config import settings

logger = logging.getLogger(__name__)

# Metadata for database operations
metadata = MetaData()

# Synchronous database engine (for migrations and sync operations)
sync_engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Asynchronous database engine (for API operations)
async_engine = create_async_engine(
    settings.get_database_url(async_driver=True),
    echo=settings.database_echo,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Session makers
SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# For backward compatibility and migrations
engine = sync_engine

def get_db() -> Session:
    """
    Dependency to get synchronous database session
    Used for backward compatibility and migrations
    """
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get asynchronous database session
    Primary session for API operations
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

class DatabaseManager:
    """Database management utilities"""
    
    @staticmethod
    async def create_tables():
        """Create all database tables"""
        from .models.database import Base
        
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created successfully")
    
    @staticmethod
    async def drop_tables():
        """Drop all database tables"""
        from .models.database import Base
        
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        
        logger.info("Database tables dropped successfully")
    
    @staticmethod
    async def check_connection() -> bool:
        """Check database connection"""
        try:
            async with AsyncSessionLocal() as session:
                await session.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False
    
    @staticmethod
    async def get_database_info() -> dict:
        """Get database information"""
        try:
            async with AsyncSessionLocal() as session:
                # Get database version
                result = await session.execute("SELECT version()")
                version = result.scalar()
                
                # Get database size (PostgreSQL specific)
                result = await session.execute(
                    "SELECT pg_size_pretty(pg_database_size(current_database()))"
                )
                size = result.scalar()
                
                # Get connection count
                result = await session.execute(
                    "SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()"
                )
                connections = result.scalar()
                
                return {
                    "version": version,
                    "size": size,
                    "active_connections": connections,
                    "status": "healthy"
                }
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

# Global database manager instance
db_manager = DatabaseManager()

# Database health check
async def health_check() -> dict:
    """Database health check"""
    try:
        is_connected = await db_manager.check_connection()
        if is_connected:
            info = await db_manager.get_database_info()
            return {
                "status": "healthy",
                "connected": True,
                **info
            }
        else:
            return {
                "status": "unhealthy",
                "connected": False,
                "error": "Connection failed"
            }
    except Exception as e:
        return {
            "status": "error",
            "connected": False,
            "error": str(e)
        }

# Transaction management utilities
class DatabaseTransaction:
    """Context manager for database transactions"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def __aenter__(self):
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.session.rollback()
            logger.error(f"Transaction rolled back due to: {exc_val}")
        else:
            await self.session.commit()

async def get_transaction(session: AsyncSession = None) -> DatabaseTransaction:
    """Get a database transaction context manager"""
    if session is None:
        session = AsyncSessionLocal()
    return DatabaseTransaction(session)

# Repository base class
class BaseRepository:
    """Base repository class with common database operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def commit(self):
        """Commit the current transaction"""
        await self.session.commit()
    
    async def rollback(self):
        """Rollback the current transaction"""
        await self.session.rollback()
    
    async def refresh(self, instance):
        """Refresh an instance from the database"""
        await self.session.refresh(instance)
    
    async def flush(self):
        """Flush pending changes to the database"""
        await self.session.flush()

# Connection pool monitoring
class ConnectionPoolMonitor:
    """Monitor database connection pool"""
    
    @staticmethod
    def get_pool_status() -> dict:
        """Get connection pool status"""
        pool = sync_engine.pool
        return {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid()
        }
    
    @staticmethod
    async def get_async_pool_status() -> dict:
        """Get async connection pool status"""
        pool = async_engine.pool
        return {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid()
        }

# Global connection pool monitor
pool_monitor = ConnectionPoolMonitor()
