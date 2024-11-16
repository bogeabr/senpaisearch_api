from http import HTTPStatus

from senpaisearch.schemas import UserPublic


def test_create_user(client, token):
    response = client.post(
        '/users/',
        json={
            'username': 'bogea',
            'password': 'bogea123',
            'email': 'bogea@gmail.com',
            'role': 'admin',
        },
        headers={'Authorization': f'Bearer {token}'},
    )
    # Voltou o status code correto?
    assert response.status_code == HTTPStatus.CREATED


def test_read_users(client, token):
    response = client.get(
        '/users',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK


def test_read_users_with_user(client, user, token):
    # Extrai apenas os campos esperados por UserPublic
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
    }

    user_schema = UserPublic(**user_data).model_dump()

    response = client.get(
        '/users/',
        headers={'Authorization': f'Bearer {token}'},
    )

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


def test_error_update_user_not_enough_permissons(
    client, user_fun, token_user_fun
):
    response = client.put(
        f'/users/{user_fun.id}',
        headers={'Authorization': f'Bearer {token_user_fun}'},
        json={
            'username': 'yasuo',
            'email': 'yasuo@gmail.com',
            'password': 'yasuo12',
        },
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_delete_wrong_user(client, user_fun, token):
    response = client.delete(
        f'/users/{user_fun.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.json() == {'message': 'User deleted'}


def test_create_user_should_retrun_400_username_exists(client, user, token):
    response = client.post(
        '/users/',
        json={
            'username': user.username,
            'password': 'bogea123',
            'email': 'bogea@gmail.com',
        },
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Username already exists'}


def test_create_user_should_retrun_400_email_exists(client, user, token):
    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'password': 'bogea123',
            'email': user.email,
            'role': 'admin',
        },
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Email already exists'}
