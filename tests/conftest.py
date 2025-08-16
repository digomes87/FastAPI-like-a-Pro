from datetime import datetime
from contextlib import contextmanager
from typing import Generator, Any, Type
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.orm import Mapper
from sqlalchemy.engine import Connection

from fast_zero.app import app

def get_client() -> TestClient:
    return TestClient(app)


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
        mapper: Mapper[Any], 
        connection: Connection, 
        target: Any
    ) -> None:
        if hasattr(target, 'created_at'):
            setattr(target, 'created_at', time)
        if hasattr(target, 'create_at'):
            setattr(target, 'create_at', time)

    event.listen(model, 'before_insert', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)


def test_example_with_mocked_time(client: TestClient) -> None:
    from fast_zero.models import User  # Import your model

    test_time = datetime(2023, 12, 25, 12, 0, 0)

    with mock_db_time(model=User, time=test_time):
        response = client.post(
            "/users/",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "secret",
            },
        )

    assert response.status_code == 201
