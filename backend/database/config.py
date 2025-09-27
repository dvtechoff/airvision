"""
Database configuration and connection management
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from contextlib import contextmanager, asynccontextmanager
from models.database import Base
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.database_url = self._get_database_url()
        self.async_database_url = self._get_async_database_url()
        
        # Create engines
        self.engine = create_engine(self.database_url, echo=False)
        self.async_engine = create_async_engine(self.async_database_url, echo=False)
        
        # Create session factories
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.AsyncSessionLocal = async_sessionmaker(self.async_engine, class_=AsyncSession, expire_on_commit=False)
        
    def _get_database_url(self) -> str:
        """Get database URL from environment or use default"""
        # Try environment variables first
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            return db_url
            
        # Construct from individual components
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        database = os.getenv("DB_NAME", "airvision")
        username = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "password")
        
        return f"postgresql://{username}:{password}@{host}:{port}/{database}"
    
    def _get_async_database_url(self) -> str:
        """Get async database URL"""
        sync_url = self._get_database_url()
        return sync_url.replace("postgresql://", "postgresql+asyncpg://")
    
    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    @contextmanager
    def get_session(self):
        """Get database session context manager"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    @asynccontextmanager
    async def get_async_session(self):
        """Get async database session context manager"""
        session = self.AsyncSessionLocal()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Global database manager instance
db_manager = DatabaseManager()

# Dependency for FastAPI
def get_database_session():
    """Dependency to get database session in FastAPI routes"""
    with db_manager.get_session() as session:
        yield session

async def get_async_database_session():
    """Async dependency to get database session in FastAPI routes"""
    async with db_manager.get_async_session() as session:
        yield session