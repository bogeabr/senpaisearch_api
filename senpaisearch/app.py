import os
from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from senpaisearch.database import get_session
from senpaisearch.models import Character
from senpaisearch.routers import auth, characters, users

app = FastAPI()
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(characters.router)

T_Session = Annotated[Session, Depends(get_session)]

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
def home(
    request: Request,
    session: T_Session,
    anime: str = None,
    hierarchy: str = None,
):
    # Busca por personagens no banco de dados
    query = session.query(Character)

    if anime:
        query = query.filter(Character.anime.contains(anime))
    if hierarchy:
        query = query.filter(Character.hierarchy.contains(hierarchy))

    characters = query.all()

    context = {
        'request': request,
        'characters': characters,
        'anime': anime,
        'hierarchy': hierarchy,
    }
    return templates.TemplateResponse('index.html', context)
