import uuid as _uuid
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from model.entity.user import User


class Account(SQLModel, table=True):
    """Login credentials mapped to 'accounts' table."""

    __tablename__ = "accounts"

    account_id: _uuid.UUID = Field(default_factory=_uuid.uuid4, primary_key=True)
    account_name: str = Field(unique=True, index=True, max_length=255)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    user_id: _uuid.UUID = Field(foreign_key="users.user_id")

    # Relationships
    user: Optional["User"] = Relationship(back_populates="accounts")
    refresh_tokens: list["RefreshToken"] = Relationship(back_populates="account")
