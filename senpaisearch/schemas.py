from typing import Optional

from pydantic import BaseModel, EmailStr


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = 'admin'


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True


class UserList(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    access_token: str  # O token jwt que vai ser gerado
    token_type: str  # O modelo que o cliente deve usar para Autorização


# Classe base com os dados principais do personagem
class CharacterBase(BaseModel):
    name: str
    age: Optional[int] = None
    anime: str
    hierarchy: str
    abilities: str
    notable_moments: str


# Classe usada para criação de novos personagens
class CharacterCreate(CharacterBase):
    pass


# Classe pública herdando de CharacterBase
class CharacterPublic(CharacterBase):
    id: int


class CharacterList(BaseModel):
    characters: list[CharacterPublic]


class CharacterUpdate(BaseModel):
    name: str | None = None
    age: str | None = None
    anime: str | None = None
    hierarchy: str | None = None
    abilities: str | None = None
    notable_moments: str | None = None
