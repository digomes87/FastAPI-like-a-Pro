from datetime import timedelta
from http import HTTPStatus
from math import ceil
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.async_auth import authenticate_user, create_access_token, get_current_user
from fast_zero.async_services import get_async_user_service
from fast_zero.database import get_async_session
from fast_zero.models import User
from fast_zero.schemas import (
    Message,
    Token,
    UserCreate,
    UserList,
    UserPublic,
    UserUpdate,
)
from fast_zero.settings import get_settings

settings = get_settings()

app = FastAPI(
    title=f"{settings.APP_NAME} (Async)",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)


@app.get(
    '/',
    status_code=HTTPStatus.OK,
    response_model=Message,
    summary='Root endpoint',
    description='Simple root endpoint'
)
async def read_root():
    """Root endpoint."""
    return {'message': 'Bora pra mais uma (Async version!)'}


@app.get(
    '/health',
    status_code=HTTPStatus.OK,
    response_model=Message,
    summary='Health check',
    description='Health check endpoint for Docker and monitoring'
)
async def health_check():
    """Health check endpoint for Docker and monitoring."""
    return {'message': 'OK'}


@app.post(
    '/users/',
    status_code=HTTPStatus.CREATED,
    response_model=UserPublic,
    summary='Create user',
    description='Create a new user account'
)
async def create_user(
    user: UserCreate,
    session: Annotated[AsyncSession, Depends(get_async_session)]
):
    """Create a new user asynchronously.
    
    Args:
        user: User creation data
        session: Async database session
        
    Returns:
        Created user information
        
    Raises:
        HTTPException: If username or email already exists
    """
    user_service = get_async_user_service(session)
    
    try:
        db_user = await user_service.create_user(user)
        return db_user
    except ValueError as e:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=str(e)
        ) from e


@app.post(
    '/auth/token',
    response_model=Token,
    summary='Login for access token',
    description='Authenticate user and return JWT access token'
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_async_session)]
):
    """Authenticate user and return access token asynchronously.
    
    Args:
        form_data: OAuth2 form data with username and password
        session: Async database session
        
    Returns:
        JWT access token
        
    Raises:
        HTTPException: If authentication fails
    """
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get(
    '/users/',
    response_model=UserList,
    summary='List users',
    description='Get paginated list of users'
)
async def read_users(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10
):
    """Get paginated list of users asynchronously.
    
    Args:
        skip: Number of users to skip
        limit: Maximum number of users to return
        session: Async database session
        
    Returns:
        Paginated list of users
    """
    user_service = get_async_user_service(session)
    
    users = await user_service.get_users(skip=skip, limit=limit)
    total = await user_service.count_users()
    
    return UserList(
        users=users,
        total=total,
        page=(skip // limit) + 1,
        per_page=limit,
        pages=ceil(total / limit) if total > 0 else 1
    )


@app.get(
    '/users/me',
    response_model=UserPublic,
    summary='Get current user',
    description='Get current authenticated user information'
)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Get current authenticated user information asynchronously.
    
    Args:
        current_user: Current authenticated user from JWT token
        
    Returns:
        Current user information
    """
    return current_user


@app.get(
    '/users/{user_id}',
    response_model=UserPublic,
    summary='Get user',
    description='Get user by ID'
)
async def read_user(
    user_id: int,
    session: Annotated[AsyncSession, Depends(get_async_session)]
):
    """Get user by ID asynchronously.
    
    Args:
        user_id: User ID
        session: Async database session
        
    Returns:
        User information
        
    Raises:
        HTTPException: If user not found
    """
    user_service = get_async_user_service(session)
    
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found'
        )
    
    return user


@app.put(
    '/users/{user_id}',
    response_model=UserPublic,
    summary='Update user',
    description='Update user information'
)
async def update_user(
    user_id: int,
    user: UserUpdate,
    session: Annotated[AsyncSession, Depends(get_async_session)]
):
    """Update user information asynchronously.
    
    Args:
        user_id: User ID
        user: User update data
        session: Async database session
        
    Returns:
        Updated user information
        
    Raises:
        HTTPException: If user not found or validation error
    """
    user_service = get_async_user_service(session)
    
    try:
        updated_user = await user_service.update_user(user_id, user)
        if not updated_user:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='User not found'
            )
        
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=str(e)
        ) from e


@app.delete(
    '/users/{user_id}',
    response_model=Message,
    summary='Delete user',
    description='Delete user by ID'
)
async def delete_user(
    user_id: int,
    session: Annotated[AsyncSession, Depends(get_async_session)]
):
    """Delete user by ID asynchronously.
    
    Args:
        user_id: User ID
        session: Async database session
        
    Returns:
        Deletion confirmation message
        
    Raises:
        HTTPException: If user not found
    """
    user_service = get_async_user_service(session)
    
    if not await user_service.delete_user(user_id):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found'
        )
    
    return {'message': 'User deleted'}