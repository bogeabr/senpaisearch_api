from http import HTTPStatus


def test_home_deve_retornar_OK(client):
    response = client.get('/')  # Act (Excuta o teste)
    assert response.status_code == HTTPStatus.OK  # Assert (Afirmação do teste)
    assert '<title>Home - SenpaiSearch</title>' in response.text
