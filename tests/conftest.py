import pytest
from fastapi.testclient import TestClient

from senpaisearch.app import app


@pytest.fixture
def client():
    return TestClient(app)
