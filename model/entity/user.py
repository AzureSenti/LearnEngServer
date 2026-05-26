import uuid as _uuid
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    """User profile mapped to 'users' table."""

    __tablename__ = "users"

    user_id: _uuid.UUID = Field(default_factory=_uuid.uuid4, primary_key=True)
    full_name: str = Field(max_length=100)
    avatar_url: str = Field(default="", max_length=500)
    coins: int = Field(default=0)
    current_streak: int = Field(default=0)
    longest_streak: int = Field(default=0)

    # Relationships
    accounts: list["Account"] = Relationship(back_populates="user")
    word_sets: list["UserWordSetCrossRef"] = Relationship(back_populates="user")
