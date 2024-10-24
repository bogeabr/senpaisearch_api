from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
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


@router.post('/', response_model=CharacterPublic)
def create_character(
    character: CharacterCreate,
    session: Session,
    user: CurrentUser,
):
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
    user: CurrentUser,
    anime: str | None = None,
    hierarchy: str | None = None,
    limit: int | None = None,
):
    query = select(Character).where(Character.user_id == user.id)

    if anime:
        query = query.filter(Character.anime.contains(anime))
    if hierarchy:
        query = query.filter(Character.hierarchy.contains(hierarchy))

    characters = session.scalars(query.limit(limit)).all()

    return {'characters': characters}


@router.delete('/{character_id}', response_model=Message)
def delete_character(
    character_id: int,
    session: Session,
    user: CurrentUser,
):
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
    db_character = session.scalar(
        select(Character).where(Character.user_id == user.id)
    )
    if not db_character:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Character not found.'
        )
    for key, value in character.model_dump(exclude_unset=True).items():
        setattr(db_character, key, value)

    session.add(db_character)
    session.commit()
    session.refresh(db_character)

    return db_character
