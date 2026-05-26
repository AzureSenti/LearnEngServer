import uuid as _uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from model.entity.account import Account


class RefreshToken(SQLModel, table=True):
    """Refresh token record mapped to 'refresh_tokens' table."""

    __tablename__ = "refresh_tokens"

    id: _uuid.UUID = Field(default_factory=_uuid.uuid4, primary_key=True)
    account_id: _uuid.UUID = Field(foreign_key="accounts.account_id")
    token: str = Field(index=True)
    expires_at: datetime = Field()
    is_revoked: bool = Field(default=False)

    # Relationships
    account: Optional["Account"] = Relationship(back_populates="refresh_tokens")
