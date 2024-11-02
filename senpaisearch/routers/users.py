from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from senpaisearch.database import get_session
from senpaisearch.models import User
from senpaisearch.schemas import (
    Message,
    UserCreateAdmin,
    UserList,
    UserPublic,
    UserSchema,
)
from senpaisearch.security import (
    get_current_active_superuser,
    get_current_user,
    get_password_hash,
)

router = APIRouter(prefix='/users', tags=['users'])
T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]
T_CurrentSuperUser = Annotated[User, Depends(get_current_active_superuser)]


@router.get('/', response_model=UserList)
def read_users(
    session: T_Session,
    current_user: T_CurrentSuperUser,
    limit: int = 100,
    offset: int = 0,
):
    # Verificação explícita de superusuário
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permissions',
        )

    users = session.scalars(select(User).offset(offset).limit(limit)).all()

    return {'users': users}


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(
    user: UserSchema,
    session: T_Session,
):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )
    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Username already exists',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Email already exists',
            )

    db_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.post('/admin/users/')
def create_user_admin(
    user_data: UserCreateAdmin,
    session: T_Session,
    current_user: T_CurrentSuperUser,
):
    if current_user.is_superuser:
        # Apenas superusuários podem criar usuários com `is_superuser`
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password=get_password_hash(user_data.password),
            is_superuser=user_data.is_superuser,
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user
    else:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='User does not have the required superuser privileges',
        )


@router.put('/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: T_Session,
    current_user: T_CurrentSuperUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    current_user.email = user.email
    current_user.username = user.username
    current_user.password = user.password

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return current_user


@router.delete('/{user_id}', response_model=Message)
def delete_user(
    user_id: int,
    session: T_Session,
    current_user: T_CurrentSuperUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    session.delete(current_user)
    session.commit()

    return {'message': 'User deleted'}
