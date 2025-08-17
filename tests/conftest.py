# Standard Library
from contextlib import contextmanager
from datetime import datetime
from http import HTTPStatus
from typing import Any, Generator, Type

# Third-party Libraries
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapper, Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Local Imports
from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import User, table_registry
from fast_zero.settings import get_settings

settings = get_settings()


@pytest.fixture
def session() -> Generator[Session, None, None]:
    """Create a test database session."""
    engine = create_engine(
        settings.TEST_DATABASE_URL,
        connect_args={'check_same_thread': False},
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


@pytest.fixture
def client(session: Session) -> TestClient:
    """Create a test client with database session override."""
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override
    
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
                'password': 'secret',
            },
        )

    assert response.status_code == HTTPStatus.OK
