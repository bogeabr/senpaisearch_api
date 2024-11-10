import factory
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer

from senpaisearch.app import app
from senpaisearch.database import get_session
from senpaisearch.models import Character, User, table_registry
from senpaisearch.security import get_password_hash


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'test{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}+senha')


class CharacterFactory(factory.Factory):
    class Meta:
        model = Character

    name = factory.Faker('name')
    age = factory.Faker('random_int')
    anime = factory.Faker('word')
    hierarchy = factory.Faker('word')
    abilities = factory.Faker('sentence')
    notable_moments = factory.Faker('paragraph')
    user_id = 1


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override

        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:17', driver='psycopg') as postgres:
        _engine = create_engine(postgres.get_connection_url())

        with _engine.begin():
            yield _engine


@pytest.fixture
def session(engine):
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)


@pytest.fixture
def user(session):
    pwd = 'testtest'
    user = UserFactory(password=get_password_hash(pwd), role='admin')

    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = pwd

    return user


@pytest.fixture
def user_fun(session):
    password = 'testtest'
    user = UserFactory(password=get_password_hash(password), role='user')

    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = 'testtest'

    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    return response.json()['access_token']


@pytest.fixture
def token_user_fun(client, user_fun):
    response = client.post(
        '/auth/token',
        data={'username': user_fun.email, 'password': user_fun.clean_password},
    )
    return response.json()['access_token']
