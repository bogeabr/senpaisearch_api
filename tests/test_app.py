from http import HTTPStatus


def test_read_root_deve_retornar_OK(client):
    response = client.get('/')  # Act (Excuta o teste)
    assert response.status_code == HTTPStatus.OK  # Assert (Afirmação do teste)
    assert response.json() == {'message': 'Olá mundo!'}


def test_create_user(client):
    response = client.post(
        '/users/',
        json={
            'username': 'bogea',
            'password': 'bogea123',
            'email': 'bogea@gmail.com',
        },
    )
    # Voltou o status code correto?
    assert response.status_code == HTTPStatus.CREATED
    # Valiidação do UserPublic
    assert response.json() == {
        'username': 'bogea',
        'email': 'bogea@gmail.com',
        'id': 1,
    }


def test_read_users(client):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'username': 'bogea',
                'email': 'bogea@gmail.com',
                'id': 1,
            }
        ]
    }


def test_update_user(client):
    response = client.put(
        'users/1',
        json={
            'password': 'buçamole',
            'username': 'testeusername2',
            'email': 'teste@gmail.com',
            'id': 1,
        },
    )
    assert response.json() == {
        'username': 'testeusername2',
        'email': 'teste@gmail.com',
        'id': 1,
    }


def test_user_not_found(client):
    response = client.put(
        '/users/99',
        json={
            'password': 'buçamole',
            'username': 'testeusername2',
            'email': 'teste@gmail.com',
            'id': 1,
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user(client):
    response = client.delete('/users/1')

    assert response.json() == {'message': 'User deleted'}


def test_delete_user_not_found(client):
    response = client.delete('/users/99')

    assert response.status_code == HTTPStatus.NOT_FOUND
