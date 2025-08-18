from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.async_services import get_async_user_service
from fast_zero.database import get_async_session
from fast_zero.models import User
from fast_zero.password_validator import (
    password_validator,
)
from fast_zero.security import UserSecurityService
from fast_zero.settings import get_settings

settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def validate_password_strength(password: str) -> None:
    """Validate password meets security requirements.

    Args:
        password: Password to validate

    Raises:
        PasswordValidationError: If password doesn't meet requirements
    """
    password_validator.validate(password)


def get_password_strength_score(password: str) -> int:
    """Get password strength score.

    Args:
        password: Password to evaluate

    Returns:
        Strength score from 0-100
    """
    return password_validator.get_strength_score(password)


def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> str:
    """Create a JWT access token.

    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time

    Returns:
        JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)

    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def authenticate_user(
    session: AsyncSession, username_or_email: str, password: str
) -> User | bool:
    """Authenticate a user asynchronously with enhanced security.

    Args:
        session: Async database session
        username_or_email: Username or email
        password: Plain text password

    Returns:
        User instance if authentication successful, False otherwise
    """
    user_service = get_async_user_service(session)
    
    # Try to find user by username or email
    user = await user_service.get_user_by_username(username_or_email)
    if not user:
        user = await user_service.get_user_by_email(username_or_email)
    
    if not user:
        return False

    # Check user security status
    security_service = UserSecurityService(session)
    try:
        await security_service.validate_user_for_login(user.username)
    except HTTPException:
        return False

    # Verify password with timing attack protection
    if not verify_password(password, user.password):
        return False

    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> User:
    """Get current user from JWT token asynchronously.

    Args:
        token: JWT token
        session: Async database session

    Returns:
        Current user instance

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_service = get_async_user_service(session)
    user = await user_service.get_user_by_username(username)

    if user is None:
        raise credentials_exception

    return user
