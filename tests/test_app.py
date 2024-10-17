from http import HTTPStatus


def test_read_root_deve_retornar_OK(client):
    response = client.get('/')  # Act (Excuta o teste)
    assert response.status_code == HTTPStatus.OK  # Assert (Afirmação do teste)
    assert response.json() == {'message': 'Olá mundo!'}
