import os
from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from senpaisearch.database import get_session
from senpaisearch.models import User
from senpaisearch.routers import auth, characters, users
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
