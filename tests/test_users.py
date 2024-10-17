from http import HTTPStatus

from senpaisearch.schemas import UserPublic


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
    response = client.get('/users')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_with_user(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user, token):
    response = client.put(
        f'users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'password': 'buçamole',
            'username': 'testeusername2',
            'email': 'teste@gmail.com',
            'id': user.id,
        },
    )
    assert response.json() == {
        'username': 'testeusername2',
        'email': 'teste@gmail.com',
        'id': user.id,
    }


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.json() == {'message': 'User deleted'}


def test_create_user_should_retrun_400_username_exists(client, user):
    response = client.post(
        '/users/',
        json={
            'username': user.username,
            'password': 'bogea123',
            'email': 'bogea@gmail.com',
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Username already exists'}


def test_create_user_should_retrun_400_email_exists(client, user):
    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'password': 'bogea123',
            'email': user.email,
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Email already exists'}
