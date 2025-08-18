from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker

from fast_zero.models import table_registry
from fast_zero.settings import get_settings

settings = get_settings()

# Database Engine Configuration
sync_database_url = settings.DATABASE_URL
if sync_database_url.startswith('postgresql+asyncpg://'):
    sync_database_url = sync_database_url.replace(
        'postgresql+asyncpg://', 'postgresql://'
    )

engine = create_engine(
    sync_database_url,
    connect_args={},
    poolclass=None,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

# Async Database Engine Configuration
async_database_url = settings.DATABASE_URL
if async_database_url.startswith('postgresql'):
    async_database_url = async_database_url.replace(
        'postgresql://', 'postgresql+asyncpg://'
    )

async_engine = create_async_engine(
    async_database_url,
    echo=settings.DEBUG,
)

# Session Factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def create_database():
    """Create all database tables."""
    table_registry.metadata.create_all(bind=engine)


def drop_database():
    """Drop all database tables."""
    table_registry.metadata.drop_all(bind=engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency to get database session."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


class DatabaseManager:
    """Database manager for handling database operations."""

    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or settings.DATABASE_URL
        self._engine = None
        self._session_factory = None
        self._async_engine = None
        self._async_session_factory = None

    @property
    def engine(self) -> Engine:
        """Get database engine."""
        if self._engine is None:
            self._engine = create_engine(
                self.database_url,
                connect_args={},
                poolclass=None,
                echo=settings.DEBUG,
            )
        return self._engine

    @property
    def session_factory(self) -> sessionmaker[Session]:
        """Get session factory."""
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine,
            )
        return self._session_factory

    @property
    def async_engine(self):
        """Get async database engine."""
        if self._async_engine is None:
            async_url = self.database_url
            if async_url.startswith('postgresql'):
                async_url = async_url.replace(
                    'postgresql://', 'postgresql+asyncpg://'
                )

            self._async_engine = create_async_engine(
                async_url,
                echo=settings.DEBUG,
            )
        return self._async_engine

    @property
    def async_session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Get async session factory."""
        if self._async_session_factory is None:
            self._async_session_factory = async_sessionmaker(
                bind=self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
        return self._async_session_factory

    def create_tables(self):
        """Create all database tables."""
        table_registry.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """Drop all database tables."""
        table_registry.metadata.drop_all(bind=self.engine)

    def get_session(self) -> Generator[Session, None, None]:
        """Get database session."""
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session."""
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def create_tables_async(self):
        """Create all database tables asynchronously."""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(table_registry.metadata.create_all)

    async def drop_tables_async(self):
        """Drop all database tables asynchronously."""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(table_registry.metadata.drop_all)


# Global database manager instance
db_manager = DatabaseManager()
