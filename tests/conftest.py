# Standard Library
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime
from http import HTTPStatus
from typing import Any, AsyncGenerator, Generator, Type

# Third-party Libraries
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Mapper, Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Local Imports
from fast_zero.async_app import app
from fast_zero.async_auth import create_access_token, get_password_hash
from fast_zero.database import get_async_session
from fast_zero.models import User, table_registry
from fast_zero.settings import get_settings

settings = get_settings()


@pytest.fixture
def session() -> Generator[Session, None, None]:
    """Create a test database session."""
    engine = create_engine(
        settings.TEST_DATABASE_URL,
        poolclass=StaticPool,
    )
    
    # Create tables
    table_registry.metadata.create_all(engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop tables
        table_registry.metadata.drop_all(engine)


@pytest_asyncio.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test async database session."""
    # Use asyncpg for async testing with PostgreSQL
    engine = create_async_engine(
        settings.TEST_DATABASE_URL,
        poolclass=StaticPool,
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
def client(async_session: AsyncSession) -> TestClient:
    """Create a test client with async database session override."""
    async def get_async_session_override():
        yield async_session
    
    app.dependency_overrides[get_async_session] = get_async_session_override
    
    yield TestClient(app)
    
    app.dependency_overrides.clear()


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
    hashed_password = get_password_hash("testpass123")
    user = User(
        username="testuser",
        email="test@example.com",
        password=hashed_password,
        first_name="Test",
        last_name="User",
        bio="Test user bio"
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest.fixture
def token(user: User) -> str:
    """Create a JWT token for the test user."""
    return create_access_token(data={"sub": user.username})
