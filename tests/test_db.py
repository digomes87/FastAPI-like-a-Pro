from datetime import datetime

from fast_zero.models import User


def test_user_is_dataclass() -> None:
    """Verify if User is properly defined as a dataclass."""
    assert hasattr(User, '__dataclass_fields__'), (
        'User class should have dataclass fields. '
        "Make sure it's decorated with @registry.mapped_as_dataclass"
    )


class TestUser:
    """Test suite for User model."""

    @staticmethod
    def test_user_has_correct_attributes() -> None:
        """Verify if User has all expected attributes."""
        user = User(
            username='testuser',
            password='secret',
            email='test@example.com'
        )

        assert user.username == 'testuser'
        assert user.password == 'secret'
        assert user.email == 'test@example.com'
        assert user.id is None  # Should not be set on initialization
        assert isinstance(user.create_at, datetime) or user.create_at is None

    @staticmethod
    def test_user_table_name_is_correct() -> None:
        """Verify the database table name is correctly set."""
        assert User.__tablename__ == 'users'

    @staticmethod
    def test_user_string_representation() -> None:
        """Verify the string representation of User."""
        user = User(
            username='testuser',
            password='secret',
            email='test@example.com'
        )
        assert 'User' in repr(user)
        assert 'testuser' in repr(user)
        assert 'test@example.com' in repr(user)
