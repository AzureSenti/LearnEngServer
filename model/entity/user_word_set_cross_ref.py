import uuid as _uuid
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from model.entity.user import User
    from model.entity.word_set import WordSet


class UserWordSetCrossRef(SQLModel, table=True):
    """Many-to-many link between users and word_sets (unlocked sets)."""

    __tablename__ = "user_word_set_cross_ref"

    user_id: _uuid.UUID = Field(foreign_key="users.user_id", primary_key=True)
    set_id: int = Field(foreign_key="word_sets.set_id", primary_key=True)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="word_sets")
    word_set: Optional["WordSet"] = Relationship(back_populates="users")
