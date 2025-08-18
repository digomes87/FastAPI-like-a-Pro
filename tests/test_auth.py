from datetime import timedelta
from http import HTTPStatus

from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy.orm import Session

from fast_zero.app import app
from fast_zero.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    verify_password,
)
from fast_zero.models import User
from fast_zero.settings import get_settings

settings = get_settings()
client = TestClient(app)


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_password_hash_and_verify(self):
        """Test password hashing and verification."""
        password = 'testpassword123'
        hashed = get_password_hash(password)

        # Hash should be different from original password
        assert hashed != password

        # Verification should work
        assert verify_password(password, hashed) is True

        # Wrong password should fail
        assert verify_password('wrongpassword', hashed) is False


class TestJWTTokens:
    """Test JWT token creation and validation."""

    def test_create_access_token(self):
        """Test JWT token creation."""
        data = {'sub': 'testuser'}
        token = create_access_token(data)

        # Token should be a string
        assert isinstance(token, str)

        # Token should be decodable
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        assert payload['sub'] == 'testuser'
        assert 'exp' in payload

    def test_create_access_token_with_expires_delta(self):
        """Test JWT token creation with custom expiration."""
        data = {'sub': 'testuser'}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta)

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        # Check that expiration field exists
        assert 'exp' in payload
        assert payload['sub'] == 'testuser'


class TestUserAuthentication:
    """Test user authentication."""

    def test_authenticate_user_success(self, session: Session, sync_user: User):
        """Test successful user authentication."""
        # User fixture should have hashed password
        authenticated_user = authenticate_user(
            session, sync_user.username, 'testpass123'
        )

        assert authenticated_user is not False
        assert authenticated_user.username == sync_user.username
        assert authenticated_user.email == sync_user.email

    def test_authenticate_user_wrong_username(self, session: Session):
        """Test authentication with wrong username."""
        result = authenticate_user(session, 'wronguser', 'testpass123')
        assert result is False

    def test_authenticate_user_wrong_password(
        self, session: Session, sync_user: User
    ):
        """Test authentication with wrong password."""
        result = authenticate_user(session, sync_user.username, 'wrongpassword')
        assert result is False


class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_login_success(self, client: TestClient, sync_user: User):
        """Test successful login."""
        response = client.post(
            '/auth/token',
            data={'username': sync_user.username, 'password': 'testpass123'},
        )

        assert response.status_code == HTTPStatus.OK
        token_data = response.json()

        assert 'access_token' in token_data
        assert token_data['token_type'] == 'bearer'

        # Token should be valid
        token = token_data['access_token']
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        assert payload['sub'] == sync_user.email

    def test_login_wrong_username(self, client: TestClient):
        """Test login with wrong username."""
        response = client.post(
            '/auth/token',
            data={'username': 'wronguser', 'password': 'testpass123'},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert 'Incorrect username or password' in response.json()['detail']

    def test_login_wrong_password(self, client: TestClient, sync_user: User):
        """Test login with wrong password."""
        response = client.post(
            '/auth/token',
            data={'username': sync_user.username, 'password': 'wrongpassword'},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert 'Incorrect username or password' in response.json()['detail']

    def test_get_current_user_success(self, client: TestClient, token: str):
        """Test getting current user with valid token."""
        response = client.get(
            '/users/me', headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == HTTPStatus.OK
        user_data = response.json()

        assert 'username' in user_data
        assert 'email' in user_data
        assert user_data['username'] == 'testuser'

    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test getting current user with invalid token."""
        response = client.get(
            '/users/me', headers={'Authorization': 'Bearer invalid_token'}
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert 'Could not validate credentials' in response.json()['detail']

    def test_get_current_user_no_token(self, client: TestClient):
        """Test getting current user without token."""
        response = client.get('/users/me')

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert 'Not authenticated' in response.json()['detail']
