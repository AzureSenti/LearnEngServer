from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class WordSet(SQLModel, table=True):
    """Word set / vocabulary group mapped to 'word_sets' table."""

    __tablename__ = "word_sets"

    set_id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field()
    unlock_cost: int = Field(default=0)

    # Relationships
    words: list["WordSetCrossRef"] = Relationship(back_populates="word_set")
    users: list["UserWordSetCrossRef"] = Relationship(back_populates="word_set")
