import uuid as _uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKeyConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from model.entity.word import Word
    from model.entity.word_set import WordSet


class WordSetCrossRef(SQLModel, table=True):
    """Many-to-many link between words and word_sets per user."""

    __tablename__ = "word_set_cross_ref"

    user_id: _uuid.UUID = Field(primary_key=True)
    word_id: int = Field(primary_key=True)
    set_id: int = Field(primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id", "word_id"],
            ["words.user_id", "words.word_id"],
        ),
        ForeignKeyConstraint(
            ["user_id", "set_id"],
            ["word_sets.user_id", "word_sets.set_id"],
        ),
    )

    # Relationships
    word: Optional["Word"] = Relationship(back_populates="word_sets")
    word_set: Optional["WordSet"] = Relationship(back_populates="words")
