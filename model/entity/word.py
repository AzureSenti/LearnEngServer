import uuid as _uuid
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from model.entity.user import User
    from model.entity.word_set_cross_ref import WordSetCrossRef
    from model.entity.word_srs import WordSrs


class Word(SQLModel, table=True):
    """Vocabulary word mapped to 'words' table.

    Composite primary key: (user_id, word_id).
    """

    __tablename__ = "words"

    user_id: _uuid.UUID = Field(foreign_key="users.user_id", primary_key=True)
    word_id: int = Field(primary_key=True)
    english_word: str = Field()
    vietnamese_meaning: str = Field()
    audio: str = Field(default="")

    # Relationships
    user: Optional["User"] = Relationship()
    word_sets: list["WordSetCrossRef"] = Relationship(back_populates="word")
    srs_progress: list["WordSrs"] = Relationship(back_populates="word")
