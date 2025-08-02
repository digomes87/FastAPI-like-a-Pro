from http import HTTPStatus


def test_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Bora pra mais uma'}


def test_create_user(client):

    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': '123ABC',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data['username'] == 'alice'
    assert data['email'] == 'alice@example.com'
    assert 'id' in data
