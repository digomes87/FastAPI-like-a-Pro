from http import HTTPStatus

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from fast_zero.models import User


def test_root_deve_retornar_ok_e_ola_mundo(client: TestClient) -> None:
    """Test root endpoint returns correct message."""
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Bora pra mais uma (Async version!)'}


def test_create_user(client: TestClient) -> None:
    """Test user creation endpoint."""
    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'TestPass9$7!',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data['username'] == 'alice'
    assert data['email'] == 'alice@example.com'
    assert 'id' in data
    assert 'created_at' in data
    assert 'updated_at' in data
    assert data['is_active'] is True
    assert data['is_verified'] is False


def test_create_user_duplicate_username(client: TestClient) -> None:
    """Test creating user with duplicate username fails."""
    # Create first user
    client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'TestPass9$7!',
        },
    )
    
    # Try to create user with same username
    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice2@example.com',
            'password': 'TestPass9$7!',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert 'Username already exists' in response.json()['detail']


def test_create_user_duplicate_email(client: TestClient) -> None:
    """Test creating user with duplicate email fails."""
    # Create first user
    client.post(
        '/users/',
        json={
            'username': 'user1',
            'email': 'duplicate@example.com',
            'password': 'TestPass9$7!',
        },
    )
    
    # Try to create user with same email but different username
    response = client.post(
        '/users/',
        json={
            'username': 'user2',
            'email': 'duplicate@example.com',
            'password': 'TestPass9$7!',
        },
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert 'Email already exists' in response.json()['detail']


def test_read_users_empty(client: TestClient) -> None:
    """Test reading users when database is empty."""
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['users'] == []
    assert data['total'] == 0
    assert data['page'] == 1
    assert data['per_page'] == 10
    assert data['pages'] == 1


def test_read_users_with_data(client: TestClient) -> None:
    """Test reading users with data in database."""
    # Create a user first
    client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'TestPass9$7!',
        },
    )
    
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data['users']) == 1
    assert data['users'][0]['username'] == 'alice'
    assert data['users'][0]['email'] == 'alice@example.com'
    assert data['total'] == 1


def test_read_user_by_id(client: TestClient) -> None:
    """Test reading a specific user by ID."""
    # Create a user first
    create_response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'TestPass9$7!',
        },
    )
    user_id = create_response.json()['id']
    
    response = client.get(f'/users/{user_id}')
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['username'] == 'alice'
    assert data['email'] == 'alice@example.com'
    assert data['id'] == user_id


def test_read_user_not_found(client: TestClient) -> None:
    """Test reading a non-existent user returns 404."""
    response = client.get('/users/999')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert 'User not found' in response.json()['detail']


def test_update_user(client: TestClient) -> None:
    """Test updating a user."""
    # Create a user first
    create_response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'TestPass9$7!',
        },
    )
    user_id = create_response.json()['id']
    
    # Update the user
    response = client.put(
        f'/users/{user_id}',
        json={
            'username': 'alice_updated',
            'email': 'alice_updated@example.com',
            'first_name': 'Alice',
            'last_name': 'Smith',
            'bio': 'Updated bio',
        },
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['username'] == 'alice_updated'
    assert data['email'] == 'alice_updated@example.com'
    assert data['first_name'] == 'Alice'
    assert data['last_name'] == 'Smith'
    assert data['bio'] == 'Updated bio'


def test_update_user_not_found(client: TestClient) -> None:
    """Test updating a non-existent user returns 404."""
    response = client.put(
        '/users/999',
        json={
            'username': 'alice_updated',
            'email': 'alice_updated@example.com',
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert 'User not found' in response.json()['detail']


def test_delete_user(client: TestClient) -> None:
    """Test deleting a user."""
    # Create a user first
    create_response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'TestPass9$7!',
        },
    )
    user_id = create_response.json()['id']
    
    # Delete the user
    response = client.delete(f'/users/{user_id}')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}
    
    # Verify user is deleted
    get_response = client.get(f'/users/{user_id}')
    assert get_response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user_not_found(client: TestClient) -> None:
    """Test deleting a non-existent user returns 404."""
    response = client.delete('/users/999')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert 'User not found' in response.json()['detail']
