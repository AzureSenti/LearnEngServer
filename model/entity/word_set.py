import uuid as _uuid
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from model.entity.user import User
    from model.entity.user_word_set_cross_ref import UserWordSetCrossRef
    from model.entity.word_set_cross_ref import WordSetCrossRef


class WordSet(SQLModel, table=True):
    """Word set / vocabulary group mapped to 'word_sets' table.

    Composite primary key: (user_id, set_id).
    """

    __tablename__ = "word_sets"

    user_id: _uuid.UUID = Field(foreign_key="users.user_id", primary_key=True)
    set_id: int = Field(primary_key=True)
    name: str = Field()
    unlock_cost: int = Field(default=0)

    # Relationships
    user: Optional["User"] = Relationship()
    words: list["WordSetCrossRef"] = Relationship(back_populates="word_set")
    users: list["UserWordSetCrossRef"] = Relationship(back_populates="word_set")
