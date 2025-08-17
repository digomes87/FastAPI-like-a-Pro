from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from fast_zero.models import table_registry
from fast_zero.settings import get_settings

settings = get_settings()

# Database Engine Configuration
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={
        'check_same_thread': False,  # SQLite specific
    } if settings.DATABASE_URL.startswith('sqlite') else {},
    poolclass=StaticPool if settings.DATABASE_URL.startswith('sqlite') else None,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

# Session Factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@event.listens_for(Engine, 'connect')
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragmas for better performance and data integrity."""
    if 'sqlite' in str(dbapi_connection):
        cursor = dbapi_connection.cursor()
        # Enable foreign key constraints
        cursor.execute('PRAGMA foreign_keys=ON')
        # Enable WAL mode for better concurrency
        cursor.execute('PRAGMA journal_mode=WAL')
        # Set synchronous mode for better performance
        cursor.execute('PRAGMA synchronous=NORMAL')
        cursor.close()


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


class DatabaseManager:
    """Database manager for handling database operations."""
    
    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or settings.DATABASE_URL
        self._engine = None
        self._session_factory = None
    
    @property
    def engine(self) -> Engine:
        """Get database engine."""
        if self._engine is None:
            self._engine = create_engine(
                self.database_url,
                connect_args={
                    'check_same_thread': False,
                } if self.database_url.startswith('sqlite') else {},
                poolclass=StaticPool if self.database_url.startswith('sqlite') else None,
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


# Global database manager instance
db_manager = DatabaseManager()