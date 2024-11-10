import os
from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import and_
from sqlalchemy.orm import Session

from senpaisearch.database import get_session
from senpaisearch.models import Character, User
from senpaisearch.routers import auth, characters, users
from senpaisearch.schemas import CharacterFilter
from senpaisearch.security import get_current_user

app = FastAPI()
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(characters.router)

T_Session = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]

# Diretório contendo arquivos estáticos
app.mount(
    '/static',
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), 'static')),
    name='static',
)

# Diretório contendo os templates Jinja
templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), 'templates')
)


@app.get('/', status_code=HTTPStatus.OK, response_class=HTMLResponse)
def home(request: Request):
    context = {'request': request}
    return templates.TemplateResponse('index.html', context)


@app.get('/search_character', status_code=HTTPStatus.OK)
def search_character(
    session: T_Session,
    name: str = Query(...),
):
    character = (
        session.query(Character)
        .filter(Character.name.ilike(f'%{name}%'))
        .first()
    )

    if not character:
        return {'error': 'Character not found'}

    # Constrói um dicionário com os campos desejados manualmente
    character_data = {
        'id': character.id,
        'name': character.name,
        'age': character.age,
        'anime': character.anime,
        'hierarchy': character.hierarchy,
        'abilities': character.abilities,
        'notable_moments': character.notable_moments,
    }

    # Retorna o JSON com os dados necessários, sem `response_model`
    return JSONResponse(content=character_data)


@app.get('/characters/search', status_code=HTTPStatus.OK)
def search_characters(
    session: T_Session, filters: CharacterFilter = Depends()
):
    query_filters = []

    # Filtro por nome
    if filters.name:
        query_filters.append(Character.name.ilike(f'%{filters.name}%'))

    # Filtro por anime
    if filters.anime:
        query_filters.append(Character.anime.ilike(f'%{filters.anime}%'))

    # Filtro por idade com operador de comparação
    if filters.age is not None:
        if filters.age_comparison == '=':
            query_filters.append(Character.age == filters.age)
        elif filters.age_comparison == '>':
            query_filters.append(Character.age > filters.age)
        elif filters.age_comparison == '<':
            query_filters.append(Character.age < filters.age)

    # Filtro por primeira letra do nome
    if filters.first_letter:
        query_filters.append(Character.name.ilike(f'{filters.first_letter}%'))

    # Executando a consulta com os filtros
    results = session.query(Character).filter(and_(*query_filters)).all()

    if not results:
        raise HTTPException(
            status_code=404,
            detail='No characters found with specified criteria',
        )

    # Construindo o JSON de retorno sem redundância,
    # selecionando apenas os campos necessários
    characters_data = [
        {
            'id': character.id,
            'name': character.name,
            'age': character.age,
            'anime': character.anime,
            'hierarchy': character.hierarchy,
            'abilities': character.abilities,
            'notable_moments': character.notable_moments,
        }
        for character in results
    ]

    return JSONResponse(content={'characters': characters_data})
