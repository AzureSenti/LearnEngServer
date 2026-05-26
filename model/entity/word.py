from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Word(SQLModel, table=True):
    """Vocabulary word mapped to 'words' table."""

    __tablename__ = "words"

    word_id: Optional[int] = Field(default=None, primary_key=True)
    english_word: str = Field()
    vietnamese_meaning: str = Field()
    audio: str = Field(default="")

    # Relationships
    word_sets: list["WordSetCrossRef"] = Relationship(back_populates="word")
