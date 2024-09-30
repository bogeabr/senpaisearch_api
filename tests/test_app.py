from http import HTTPStatus

from fastapi.testclient import TestClient

from senpaisearch.app import app


def test_read_root_deve_retornar_OK():
    client = TestClient(app)  # Arrange (Organização do teste)
    response = client.get('/')  # Act (Excuta o teste)
    assert response.status_code == HTTPStatus.OK  # Assert (Afirmação do teste)
    assert response.json() == {'message': 'Olá mundo!'}
