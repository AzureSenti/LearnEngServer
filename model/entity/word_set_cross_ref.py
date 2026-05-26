from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from model.entity.word import Word
    from model.entity.word_set import WordSet


class WordSetCrossRef(SQLModel, table=True):
    """Many-to-many link between words and word_sets."""

    __tablename__ = "word_set_cross_ref"

    word_id: int = Field(foreign_key="words.word_id", primary_key=True)
    set_id: int = Field(foreign_key="word_sets.set_id", primary_key=True)

    # Relationships
    word: Optional["Word"] = Relationship(back_populates="word_sets")
    word_set: Optional["WordSet"] = Relationship(back_populates="words")
