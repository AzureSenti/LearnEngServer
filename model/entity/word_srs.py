import uuid as _uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKeyConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from model.entity.user import User
    from model.entity.word import Word

class WordSrs(SQLModel, table=True):
    """Spaced-repetition progress for a single word per user.

    Composite primary key: (user_id, word_id).
    """
    __tablename__ = "word_srs"

    user_id: _uuid.UUID = Field(foreign_key="users.user_id", primary_key=True)
    word_id: int = Field(primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id", "word_id"],
            ["words.user_id", "words.word_id"],
        ),
    )

    level: int = Field(default=0)
    next_review_date: int = Field(default=0, description="Epoch milliseconds")
    last_review_date: Optional[int] = Field(default=None, description="Epoch milliseconds")

    # Relationships
    user: Optional["User"] = Relationship()
    word: Optional["Word"] = Relationship()