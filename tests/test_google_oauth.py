"""Tests for Google OAuth endpoints."""
from http import HTTPStatus
from unittest.mock import Mock, patch

import pytest
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
    assert response.status_code == HTTPStatus.BAD_REQUEST
    data = response.json()
    assert 'Authorization code not provided' in data['detail']


def test_google_callback_endpoint_missing_state(client: TestClient) -> None:
    """Test Google OAuth callback endpoint without state parameter."""
    response = client.get('/auth/google/callback?code=test_code')
    assert response.status_code == HTTPStatus.BAD_REQUEST
    data = response.json()
    assert 'State parameter not provided' in data['detail']


@patch('fast_zero.google_oauth.google_oauth_client.fetch_token')
@patch('fast_zero.google_oauth.google_oauth_client.get')
def test_google_callback_endpoint_success(
    mock_get: Mock, mock_fetch_token: Mock, client: TestClient
) -> None:
    """Test successful Google OAuth callback."""
    # Mock the token fetch
    mock_fetch_token.return_value = {'access_token': 'test_token'}
    
    # Mock the user info response
    mock_response = Mock()
    mock_response.json.return_value = {
        'email': 'test@gmail.com',
        'name': 'Test User',
        'given_name': 'Test',
        'family_name': 'User',
        'picture': 'https://example.com/picture.jpg'
    }
    mock_get.return_value = mock_response
    
    response = client.get('/auth/google/callback?code=test_code&state=test_state')
    
    # Should redirect or return user info
    assert response.status_code in [HTTPStatus.OK, HTTPStatus.FOUND, HTTPStatus.TEMPORARY_REDIRECT]


@patch('fast_zero.google_oauth.google_oauth_client.fetch_token')
def test_google_callback_endpoint_token_error(
    mock_fetch_token: Mock, client: TestClient
) -> None:
    """Test Google OAuth callback with token fetch error."""
    # Mock token fetch to raise an exception
    mock_fetch_token.side_effect = Exception('Token fetch failed')
    
    response = client.get('/auth/google/callback?code=test_code&state=test_state')
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    data = response.json()
    assert 'OAuth authentication failed' in data['detail']