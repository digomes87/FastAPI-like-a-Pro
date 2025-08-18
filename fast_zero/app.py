from datetime import timedelta
from http import HTTPStatus
from math import ceil
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from fast_zero.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
)
from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import (
    Message,
    Token,
    UserCreate,
    UserList,
    UserPublic,
    UserUpdate,
)
from fast_zero.services import UserService
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
    description='Simple health check endpoint',
)
def read_root():
    """Root endpoint."""
    return {'message': 'Bora pra mais uma (Async version!)'}


@app.post(
    '/users/',
    status_code=HTTPStatus.CREATED,
    response_model=UserPublic,
    summary='Create user',
    description='Create a new user account',
)
def create_user(
    user: UserCreate,
    session: Annotated[Session, Depends(get_session)],
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
    user_service = UserService(session)

    try:
        db_user = user_service.create_user(user)
        session.commit()
        return db_user
    except ValueError as e:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail=str(e)
        ) from e


@app.post(
    '/auth/token',
    response_model=Token,
    summary='Login for access token',
    description='Authenticate user and return JWT access token',
)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)],
):
    """Authenticate user and return access token.

    Args:
        form_data: OAuth2 form data with username and password
        session: Database session

    Returns:
        JWT access token

    Raises:
        HTTPException: If authentication fails
    """
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        data={'sub': user.email}, expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


@app.get(
    '/users/',
    response_model=UserList,
    summary='List users',
    description='Get a paginated list of users',
)
def read_users(
    session: Annotated[Session, Depends(get_session)],
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 10,
):
    """Get a paginated list of users.

    Args:
        session: Database session
        page: Page number (starts from 1)
        per_page: Number of users per page (1-100)

    Returns:
        Paginated list of users
    """
    user_service = UserService(session)
    users, total = user_service.get_users(page=page, per_page=per_page)

    pages = ceil(total / per_page) if total > 0 else 1

    return UserList(
        users=users,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


@app.get(
    '/users/{user_id}',
    response_model=UserPublic,
    summary='Get user by ID',
    description='Get a specific user by their ID',
)
def read_user(
    user_id: int,
    session: Annotated[Session, Depends(get_session)],
):
    """Get a user by ID.

    Args:
        user_id: User ID
        session: Database session

    Returns:
        User information

    Raises:
        HTTPException: If user not found
    """
    user_service = UserService(session)
    user = user_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    return user


@app.put(
    '/users/{user_id}',
    response_model=UserPublic,
    summary='Update user',
    description='Update a user by their ID',
)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Update a user.

    Args:
        user_id: User ID to update
        user_update: User update data
        session: Database session
        current_user: Currently authenticated user

    Returns:
        Updated user information

    Raises:
        HTTPException: If user not found or not authorized
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    user_service = UserService(session)

    try:
        updated_user = user_service.update_user(user_id, user_update)
        if not updated_user:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail='User not found'
            )
        session.commit()
        return updated_user
    except ValueError as e:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail=str(e)
        ) from e


@app.delete(
    '/users/{user_id}',
    response_model=Message,
    summary='Delete user',
    description='Delete a user by their ID',
)
def delete_user(
    user_id: int,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Delete a user.

    Args:
        user_id: User ID to delete
        session: Database session
        current_user: Currently authenticated user

    Returns:
        Deletion confirmation message

    Raises:
        HTTPException: If user not found or not authorized
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    user_service = UserService(session)

    if not user_service.delete_user(user_id):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    session.commit()
    return {'message': 'User deleted'}
