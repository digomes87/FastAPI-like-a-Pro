"""Tests for Google OAuth endpoints."""

from http import HTTPStatus
from unittest.mock import AsyncMock, Mock, patch

from fastapi.testclient import TestClient


def test_google_login_endpoint(client: TestClient) -> None:
    """Test Google OAuth login endpoint."""
    response = client.get('/auth/google/login')
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert 'authorization_url' in data
    assert 'message' in data
    assert 'accounts.google.com' in data['authorization_url']
    assert 'Redirect to this URL' in data['message']


def test_google_callback_endpoint_missing_code(client: TestClient) -> None:
    """Test Google OAuth callback endpoint without code parameter."""
    response = client.get('/auth/google/callback')
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    data = response.json()
    assert 'detail' in data


def test_google_callback_endpoint_missing_state(client: TestClient) -> None:
    """Test Google OAuth callback endpoint without state parameter."""
    response = client.get('/auth/google/callback?code=test_code')
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    data = response.json()
    assert 'detail' in data


@patch('fast_zero.google_oauth.google_oauth.validate_user_info')
@patch('fast_zero.google_oauth.google_oauth.get_user_info')
def test_google_callback_endpoint_success(
    mock_get_user_info: AsyncMock,
    mock_validate_user_info: Mock,
    client: TestClient,
) -> None:
    """Test successful Google OAuth callback."""
    # Mock the async get_user_info method
    mock_get_user_info.return_value = {
        'email': 'test@gmail.com',
        'name': 'Test User',
        'given_name': 'Test',
        'family_name': 'User',
        'id': '123456789',
        'picture': 'https://example.com/photo.jpg',
        'verified_email': True,
    }

    # Mock the validate_user_info method
    mock_validate_user_info.return_value = {
        'email': 'test@gmail.com',
        'first_name': 'Test',
        'last_name': 'User',
        'google_id': '123456789',
        'picture': 'https://example.com/photo.jpg',
        'verified_email': True,
    }

    # Test the callback endpoint
    response = client.get('/auth/google/callback?code=test_code')
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'bearer'


@patch('fast_zero.google_oauth.google_oauth.get_user_info')
def test_google_callback_endpoint_token_error(
    mock_get_user_info: AsyncMock, client: TestClient
) -> None:
    """Test Google OAuth callback with user info fetch error."""
    # Mock async get_user_info to raise an exception
    mock_get_user_info.side_effect = Exception('User info fetch failed')

    # Test the callback endpoint
    response = client.get('/auth/google/callback?code=test_code')
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    data = response.json()
    assert 'detail' in data
