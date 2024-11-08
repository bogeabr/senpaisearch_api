import os
import time
from collections import defaultdict
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from senpaisearch.database import get_session
from senpaisearch.models import Character, User
from senpaisearch.schemas import (
    CharacterCreate,
    CharacterList,
    CharacterPublic,
    CharacterUpdate,
    Message,
)
from senpaisearch.security import get_current_user

router = APIRouter(prefix='/characters', tags=['characters'])

Session = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]

# Diretório contendo os templates Jinja
templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), '../templates')
)

# Limite de requisições e período.
RATE_LIMIT = 5
RATE_PERIOD = 60  # em segundos
request_counts = defaultdict(lambda: [0, 0])  # [contador, timestamp]


@router.post('/', response_model=CharacterPublic)
def create_character(
    character: CharacterCreate,
    session: Session,
    user: CurrentUser,
):
    # Verifica se o usuário é admin
    if user.role != 'admin':
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    # Extraindo os campos enviados
    db_character = Character(
        name=character.name,
        age=character.age,
        anime=character.anime,
        hierarchy=character.hierarchy,
        abilities=character.abilities,
        notable_moments=character.notable_moments,
        user_id=user.id,
    )
    session.add(db_character)
    session.commit()
    session.refresh(db_character)
    return db_character


@router.get('/', response_model=CharacterList)
def list_characters(
    session: Session,
    request: Request,
    get_filter: str = Query(
        None,
        description=(
            'Filtro de busca.' "Use o formato 'campo:valor', ex: 'name:Naruto'"
        ),
    ),
    limit: int | None = None,
):
    current_user = CurrentUser

    # Verificação de rate limit para usuários não autenticados
    if not (current_user and current_user.role == 'admin'):
        client_ip = request.client.host
        request_count, last_request_time = request_counts[client_ip]
        current_time = time.time()

        # Reinicia o contador se o período de limitação foi excedido
        if current_time - last_request_time > RATE_PERIOD:
            request_counts[client_ip] = [1, current_time]
        else:
            # Incrementa o contador e aplica o limite
            if request_count >= RATE_LIMIT:
                raise HTTPException(
                    status_code=HTTPStatus.TOO_MANY_REQUESTS,
                    detail='Rate limit exceeded. Try again later.',
                )
            request_counts[client_ip][0] += 1

    # Construção da consulta com filtros e limite
    query = select(Character)
    if get_filter:
        try:
            field, value = get_filter.split(':', 1)
            if field == 'name':
                query = query.filter(Character.name.contains(value))
            elif field == 'anime':
                query = query.filter(Character.anime.contains(value))
            elif field == 'age':
                query = query.filter(Character.age == int(value))
            elif field == 'hierarchy':
                query = query.filter(Character.hierarchy.contains(value))
            else:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail='Filtro inválido.'
                    "Use 'name', 'anime', 'age', ou 'hierarchy'.",
                )
        except ValueError:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="O formato do filtro deve ser 'campo:valor'.",
            )

    # Aplica a limitação de resultados se fornecida
    if limit:
        query = query.limit(limit)

    # Executa a consulta
    characters = session.scalars(query).all()

    return {'characters': characters}


@router.delete('/{character_id}', response_model=Message)
def delete_character(
    character_id: int,
    session: Session,
    user: CurrentUser,
):
    # Verifica se o usuário é admin
    if user.role != 'admin':
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    character = session.scalar(
        select(Character).where(
            Character.user_id == user.id, Character.id == character_id
        )
    )
    if not character:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Character not found',
        )
    session.delete(character)
    session.commit()

    return {'message': 'Character has been deleted successfully.'}


@router.patch('/{character_id}', response_model=CharacterPublic)
def patch_character(
    character_id: int,
    session: Session,
    user: CurrentUser,
    character: CharacterUpdate,
):
    # Verifica se o usuário é admin
    if user.role != 'admin':
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    # Busca o personagem pelo ID
    db_character = session.scalar(
        select(Character).where(Character.id == character_id)
    )
    if not db_character:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Character not found'
        )

    for key, value in character.model_dump(exclude_unset=True).items():
        setattr(db_character, key, value)

    session.add(db_character)
    session.commit()
    session.refresh(db_character)

    return db_character
