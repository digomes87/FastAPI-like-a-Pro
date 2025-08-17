from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.auth import get_password_hash
from fast_zero.models import User
from fast_zero.schemas import UserCreate, UserUpdate


class AsyncUserService:
    """Async service class for user-related operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user asynchronously.

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
            await self.session.flush()  # Flush to get the ID
            return user
        except IntegrityError as e:
            await self.session.rollback()
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

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID asynchronously.

        Args:
            user_id: User ID

        Returns:
            User instance or None if not found
        """
        return await self.session.get(User, user_id)

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username asynchronously.

        Args:
            username: Username

        Returns:
            User instance or None if not found
        """
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email asynchronously.

        Args:
            email: Email address

        Returns:
            User instance or None if not found
        """
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_users(
        self, skip: int = 0, limit: int = 100, active_only: bool = True
    ) -> Sequence[User]:
        """Get list of users with pagination asynchronously.

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
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_user(
        self, user_id: int, user_data: UserUpdate
    ) -> Optional[User]:
        """Update user information asynchronously.

        Args:
            user_id: User ID
            user_data: User update data

        Returns:
            Updated user instance or None if not found

        Raises:
            IntegrityError: If username or email already exists
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        # Update only provided fields
        update_data = user_data.model_dump(exclude_unset=True)

        try:
            for field, value in update_data.items():
                setattr(user, field, value)

            await self.session.flush()
            await self.session.refresh(user)
            return user
        except IntegrityError as e:
            await self.session.rollback()
            if 'username' in str(e):
                raise ValueError('Username already exists') from e
            elif 'email' in str(e):
                raise ValueError('Email already exists') from e
            raise e

    async def delete_user(self, user_id: int) -> bool:
        """Delete user by ID asynchronously.

        Args:
            user_id: User ID

        Returns:
            True if user was deleted, False if not found
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return False

        await self.session.delete(user)
        await self.session.flush()
        return True

    async def deactivate_user(self, user_id: int) -> Optional[User]:
        """Deactivate user (soft delete) asynchronously.

        Args:
            user_id: User ID

        Returns:
            Deactivated user instance or None if not found
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        user.is_active = False
        await self.session.flush()
        return user

    async def activate_user(self, user_id: int) -> Optional[User]:
        """Activate user asynchronously.

        Args:
            user_id: User ID

        Returns:
            Activated user instance or None if not found
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        user.is_active = True
        await self.session.flush()
        return user

    async def count_users(self, active_only: bool = True) -> int:
        """Count total number of users asynchronously.

        Args:
            active_only: Whether to count only active users

        Returns:
            Total number of users
        """
        stmt = select(User)

        if active_only:
            stmt = stmt.where(User.is_active)

        result = await self.session.execute(stmt)
        return len(result.scalars().all())

    async def get_user_by_google_id(self, google_id: str) -> Optional[User]:
        """Get user by Google ID asynchronously.

        Args:
            google_id: Google OAuth user ID

        Returns:
            User instance or None if not found
        """
        stmt = select(User).where(User.google_id == google_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_oauth_user(
        self,
        user_data: UserCreate,
        google_id: str,
        picture: str = '',
        oauth_provider: str = 'google',
        is_verified: bool = False,
    ) -> User:
        """Create a new OAuth user asynchronously.

        Args:
            user_data: User creation data
            google_id: Google OAuth user ID
            picture: User profile picture URL
            oauth_provider: OAuth provider name
            is_verified: Whether email is verified

        Returns:
            Created user instance

        Raises:
            IntegrityError: If username or email already exists
        """
        # For OAuth users, password can be empty
        hashed_password = (
            get_password_hash(user_data.password)
            if user_data.password
            else None
        )

        user = User(
            username=user_data.username,
            email=user_data.email,
            password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            bio=user_data.bio,
            google_id=google_id,
            picture=picture,
            oauth_provider=oauth_provider,
            is_verified=is_verified,
            is_active=True,
        )

        try:
            self.session.add(user)
            await self.session.flush()  # Flush to get the ID
            return user
        except IntegrityError as e:
            await self.session.rollback()
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

    async def update_user_oauth_info(
        self,
        user_id: int,
        google_id: str,
        picture: str = '',
        oauth_provider: str = 'google',
    ) -> Optional[User]:
        """Update user OAuth information asynchronously.

        Args:
            user_id: User ID
            google_id: Google OAuth user ID
            picture: User profile picture URL
            oauth_provider: OAuth provider name

        Returns:
            Updated user instance or None if not found
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        user.google_id = google_id
        user.picture = picture
        user.oauth_provider = oauth_provider

        await self.session.flush()
        await self.session.refresh(user)
        return user


def get_async_user_service(session: AsyncSession) -> AsyncUserService:
    """Get async user service instance.

    Args:
        session: Async database session

    Returns:
        AsyncUserService instance
    """
    return AsyncUserService(session)
