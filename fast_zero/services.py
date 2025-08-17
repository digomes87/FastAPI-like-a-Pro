from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_zero.auth import get_password_hash
from fast_zero.models import User
from fast_zero.schemas import UserCreate, UserUpdate


class UserService:
    """Service class for user-related operations."""

    def __init__(self, session: Session):
        self.session = session

    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user.

        Args:
            user_data: User creation data

        Returns:
            Created user instance

        Raises:
            IntegrityError: If username or email already exists
        """
        # Hash password before storing
        hashed_password = get_password_hash(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            bio=user_data.bio,
        )

        try:
            self.session.add(user)
            self.session.flush()  # Flush to get the ID
            return user
        except IntegrityError as e:
            self.session.rollback()
            error_msg = str(e).lower()
            # Check for specific constraint violations
            if (
                'users.username' in error_msg
                or 'unique constraint failed: users.username' in error_msg
            ):
                raise ValueError('Username already exists') from e
            elif (
                'users.email' in error_msg
                or 'unique constraint failed: users.email' in error_msg
            ):
                raise ValueError('Email already exists') from e
            elif 'username' in error_msg:
                raise ValueError('Username already exists') from e
            elif 'email' in error_msg:
                raise ValueError('Email already exists') from e
            raise e

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User instance or None if not found
        """
        return self.session.get(User, user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username.

        Args:
            username: Username

        Returns:
            User instance or None if not found
        """
        stmt = select(User).where(User.username == username)
        return self.session.scalar(stmt)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email.

        Args:
            email: Email address

        Returns:
            User instance or None if not found
        """
        stmt = select(User).where(User.email == email)
        return self.session.scalar(stmt)

    def get_users(
        self, skip: int = 0, limit: int = 100, active_only: bool = True
    ) -> Sequence[User]:
        """Get list of users with pagination.

        Args:
            skip: Number of users to skip
            limit: Maximum number of users to return
            active_only: Whether to return only active users

        Returns:
            List of users
        """
        stmt = select(User)

        if active_only:
            stmt = stmt.where(User.is_active)

        stmt = stmt.offset(skip).limit(limit)
        return self.session.scalars(stmt).all()

    def update_user(
        self, user_id: int, user_data: UserUpdate
    ) -> Optional[User]:
        """Update user information.

        Args:
            user_id: User ID
            user_data: User update data

        Returns:
            Updated user instance or None if not found

        Raises:
            IntegrityError: If username or email already exists
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        # Update only provided fields
        update_data = user_data.model_dump(exclude_unset=True)

        try:
            for field, value in update_data.items():
                setattr(user, field, value)

            self.session.flush()
            return user
        except IntegrityError as e:
            self.session.rollback()
            if 'username' in str(e):
                raise ValueError('Username already exists') from e
            elif 'email' in str(e):
                raise ValueError('Email already exists') from e
            raise e

    def delete_user(self, user_id: int) -> bool:
        """Delete user by ID.

        Args:
            user_id: User ID

        Returns:
            True if user was deleted, False if not found
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        self.session.delete(user)
        self.session.flush()
        return True

    def deactivate_user(self, user_id: int) -> Optional[User]:
        """Deactivate user (soft delete).

        Args:
            user_id: User ID

        Returns:
            Deactivated user instance or None if not found
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        user.is_active = False
        self.session.flush()
        return user

    def activate_user(self, user_id: int) -> Optional[User]:
        """Activate user.

        Args:
            user_id: User ID

        Returns:
            Activated user instance or None if not found
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        user.is_active = True
        self.session.flush()
        return user

    def count_users(self, active_only: bool = True) -> int:
        """Count total number of users.

        Args:
            active_only: Whether to count only active users

        Returns:
            Total number of users
        """
        stmt = select(User)

        if active_only:
            stmt = stmt.where(User.is_active)

        return len(self.session.scalars(stmt).all())


def get_user_service(session: Session) -> UserService:
    """Get user service instance.

    Args:
        session: Database session

    Returns:
        UserService instance
    """
    return UserService(session)
