import uuid as _uuid
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from model.entity.user import User


class UserGrammarProgress(SQLModel, table=True):
    """Grammar lesson progress per user.

    Composite primary key: (user_id, lesson_id).
    """

    __tablename__ = "user_grammar_progress"

    user_id: _uuid.UUID = Field(foreign_key="users.user_id", primary_key=True)
    lesson_id: int = Field(primary_key=True)
    is_theory_completed: bool = Field(default=False)
    is_quiz_passed: bool = Field(default=False)
    score: int = Field(default=0)

    # Relationships
    user: Optional["User"] = Relationship()
