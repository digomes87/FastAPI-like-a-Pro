# Standard Library
from contextlib import contextmanager
from datetime import datetime
from http import HTTPStatus
from typing import Any, AsyncGenerator, Generator, Type

# Third-party Libraries
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Mapper, Session, sessionmaker


# Local Imports
from fast_zero.app import app as sync_app
from fast_zero.async_app import app as async_app
from fast_zero.auth import create_access_token, get_password_hash
from fast_zero.database import get_async_session
from fast_zero.models import User, table_registry
from fast_zero.settings import get_settings

settings = get_settings()


@pytest.fixture
def session() -> Generator[Session, None, None]:
    """Create a test database session."""
    # Use psycopg2 for sync testing with PostgreSQL
    sync_database_url = settings.TEST_DATABASE_URL
    if sync_database_url.startswith('postgresql+asyncpg://'):
        sync_database_url = sync_database_url.replace(
            'postgresql+asyncpg://', 'postgresql://'
        )
    
    engine = create_engine(
        sync_database_url,
        echo=False,
    )

    # Create tables once
    table_registry.metadata.create_all(engine)

    # Create session with transaction
    connection = engine.connect()
    transaction = connection.begin()
    
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=connection
    )

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest_asyncio.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test async database session."""
    # Use asyncpg for async testing with PostgreSQL
    async_database_url = settings.TEST_DATABASE_URL
    if async_database_url.startswith('postgresql://'):
        async_database_url = async_database_url.replace(
            'postgresql://', 'postgresql+asyncpg://'
        )
    engine = create_async_engine(
        async_database_url,
        echo=False,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    # Create session
    AsyncTestingSessionLocal = async_sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )

    async with AsyncTestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def client(session: Session) -> TestClient:
    """Create a test client with database session override."""
    from fast_zero.database import get_session
    
    def get_session_override():
        return session

    sync_app.dependency_overrides[get_session] = get_session_override

    with TestClient(sync_app) as test_client:
        yield test_client

    sync_app.dependency_overrides.clear()


@pytest.fixture
def async_client(async_session: AsyncSession) -> TestClient:
    """Create a test client with async database session override."""

    def get_async_session_override():
        return async_session

    async_app.dependency_overrides[get_async_session] = get_async_session_override

    with TestClient(async_app) as test_client:
        yield test_client

    async_app.dependency_overrides.clear()


@contextmanager
def mock_db_time(
    *, model: Type[Any], time: datetime = datetime(2024, 1, 1)
) -> Generator[datetime, None, None]:
    """
    Context manager to mock the created_at timestamp for a SQLAlchemy model.

    Usage:
    with mock_db_time(model=User, time=desired_datetime):
        # Your test code here
    """

    def fake_time_hook(
        mapper: Mapper[Any], connection: Connection, target: Any
    ) -> None:
        if hasattr(target, 'created_at'):
            setattr(target, 'created_at', time)
        if hasattr(target, 'create_at'):
            setattr(target, 'create_at', time)

    event.listen(model, 'before_insert', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)


def test_example_with_mocked_time(client: TestClient) -> None:
    test_time = datetime(2023, 12, 25, 12, 0, 0)

    with mock_db_time(model=User, time=test_time):
        response = client.post(
            '/users/',
            json={
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'TestPass9$7!',
            },
        )

    assert response.status_code == HTTPStatus.OK


@pytest_asyncio.fixture
async def user(async_session: AsyncSession) -> User:
    """Create a test user with hashed password asynchronously."""
    hashed_password = get_password_hash('testpass123')
    user = User(
        username='testuser',
        email='test@example.com',
        password=hashed_password,
        first_name='Test',
        last_name='User',
        bio='Test user bio',
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest.fixture
def sync_user(session: Session) -> User:
    """Create a test user with hashed password synchronously."""
    hashed_password = get_password_hash('testpass123')
    user = User(
        username='testuser',
        email='test@example.com',
        password=hashed_password,
        first_name='Test',
        last_name='User',
        bio='Test user bio',
    )
    session.add(user)
    session.flush()  # Flush instead of commit to keep in transaction
    session.refresh(user)
    return user


@pytest.fixture
def token(sync_user: User) -> str:
    """Create a JWT token for the test user."""
    return create_access_token(data={'sub': sync_user.email})
