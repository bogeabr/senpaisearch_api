from datetime import datetime

from sqlalchemy import INTEGER, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, registry

table_registry = registry()


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    role: Mapped[str] = mapped_column(default='admin')
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    update_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )


@table_registry.mapped_as_dataclass
class Character:
    __tablename__ = 'characters'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    age: Mapped[int] = mapped_column(INTEGER, nullable=True)
    anime: Mapped[str] = mapped_column(String, nullable=False)
    hierarchy: Mapped[str] = mapped_column(String, nullable=False)
    abilities: Mapped[str]
    notable_moments: Mapped[str]

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
