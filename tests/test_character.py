from http import HTTPStatus

from tests.conftest import CharacterFactory


def test_create_character(client, token):
    response = client.post(
        '/characters/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'tales',
            'age': 29,
            'anime': 'entropia',
            'hierarchy': 'Vilão',
            'abilities': 'Domínio quantico, MMA',
            'notable_moments': 'Eliminou 17 traficantes apenas com as mãos',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'name': 'tales',
        'age': 29,
        'anime': 'entropia',
        'hierarchy': 'Vilão',
        'abilities': 'Domínio quantico, MMA',
        'notable_moments': 'Eliminou 17 traficantes apenas com as mãos',
    }


def test_list_characters_should_return_5_characters(
    session,
    client,
    user,
    token,
):
    expected_characters = 5
    session.bulk_save_objects(
        CharacterFactory.create_batch(5, user_id=user.id)
    )
    session.commit()

    response = client.get(
        '/characters/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['characters']) == expected_characters


def test_list_characters_pagination_should_return_2_characters(
    session,
    client,
    user,
    token,
):
    expected_characters = 2
    session.bulk_save_objects(
        CharacterFactory.create_batch(5, user_id=user.id)
    )
    session.commit()

    response = client.get(
        '/characters/?limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['characters']) == expected_characters


def test_list_characters_filter_anime_should_return_5_characters(
    session,
    client,
    user,
    token,
):
    expected_characters = 5
    session.bulk_save_objects(
        CharacterFactory.create_batch(5, user_id=user.id, anime='Monogatari 1')
    )
    session.commit()

    response = client.get(
        '/characters/?anime=Monogatari 1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['characters']) == expected_characters


def test_list_characters_filter_hierarchy_should_return_5_characters(
    session,
    client,
    user,
    token,
):
    expected_characters = 5
    session.bulk_save_objects(
        CharacterFactory.create_batch(5, user_id=user.id, hierarchy='Vilão')
    )
    session.commit()

    response = client.get(
        '/characters/?hierarchy=Vilão',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['characters']) == expected_characters


def test_delete_character(session, client, user, token):
    character = CharacterFactory(user_id=user.id)
    session.add(character)
    session.commit()
    session.refresh(character)

    response = client.delete(
        f'/characters/{character.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'message': 'Character has been deleted successfully.'
    }


def test_delete_character_error(client, token):
    response = client.delete(
        f'/characters/{10}', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Character not found'}


def test_patch_character_error(client, token):
    response = client.patch(
        '/characters/10',
        json={},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Character not found'}


def test_patch_character(session, client, user, token):
    character = CharacterFactory(user_id=user.id)
    session.add(character)
    session.commit()
    session.refresh(character)

    response = client.patch(
        f'/characters/{character.id}',
        json={'name': 'teste1'},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['name'] == 'teste1'
