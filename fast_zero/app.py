from http import HTTPStatus
from math import ceil
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.schemas import (
    Message,
    UserCreate,
    UserList,
    UserPublic,
    UserUpdate,
)
from fast_zero.services import get_user_service
from fast_zero.settings import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)


@app.get(
    '/',
    status_code=HTTPStatus.OK,
    response_model=Message,
    summary='Health check',
    description='Simple health check endpoint'
)
def read_root():
    """Health check endpoint."""
    return {'message': 'Bora pra mais uma'}


@app.post(
    '/users/',
    status_code=HTTPStatus.CREATED,
    response_model=UserPublic,
    summary='Create user',
    description='Create a new user account'
)
def create_user(
    user: UserCreate,
    session: Annotated[Session, Depends(get_session)]
):
    """Create a new user.
    
    Args:
        user: User creation data
        session: Database session
        
    Returns:
        Created user information
        
    Raises:
        HTTPException: If username or email already exists
    """
    user_service = get_user_service(session)
    
    try:
        db_user = user_service.create_user(user)
        return db_user
    except ValueError as e:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=str(e)
        ) from e


@app.get(
    '/users/',
    response_model=UserList,
    summary='List users',
    description='Get paginated list of users'
)
def read_users(
    session: Annotated[Session, Depends(get_session)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10
):
    """Get paginated list of users.
    
    Args:
        skip: Number of users to skip
        limit: Maximum number of users to return
        session: Database session
        
    Returns:
        Paginated list of users
    """
    user_service = get_user_service(session)
    
    users = user_service.get_users(skip=skip, limit=limit)
    total = user_service.count_users()
    
    return UserList(
        users=users,
        total=total,
        page=(skip // limit) + 1,
        per_page=limit,
        pages=ceil(total / limit) if total > 0 else 1
    )


@app.get(
    '/users/{user_id}',
    response_model=UserPublic,
    summary='Get user',
    description='Get user by ID'
)
def read_user(
    user_id: int,
    session: Annotated[Session, Depends(get_session)]
):
    """Get user by ID.
    
    Args:
        user_id: User ID
        session: Database session
        
    Returns:
        User information
        
    Raises:
        HTTPException: If user not found
    """
    user_service = get_user_service(session)
    
    user = user_service.get_user_by_id(user_id)
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
def update_user(
    user_id: int,
    user: UserUpdate,
    session: Annotated[Session, Depends(get_session)]
):
    """Update user information.
    
    Args:
        user_id: User ID
        user: User update data
        session: Database session
        
    Returns:
        Updated user information
        
    Raises:
        HTTPException: If user not found or validation error
    """
    user_service = get_user_service(session)
    
    try:
        updated_user = user_service.update_user(user_id, user)
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
def delete_user(
    user_id: int,
    session: Annotated[Session, Depends(get_session)]
):
    """Delete user by ID.
    
    Args:
        user_id: User ID
        session: Database session
        
    Returns:
        Deletion confirmation message
        
    Raises:
        HTTPException: If user not found
    """
    user_service = get_user_service(session)
    
    if not user_service.delete_user(user_id):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='User not found'
        )
    
    return {'message': 'User deleted'}
