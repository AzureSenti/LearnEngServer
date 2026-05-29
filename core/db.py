from sqlmodel import Session, SQLModel, create_engine

from core.config import settings

engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    connect_args={"prepare_threshold": None},
)


def init_db() -> None:
    """Create all tables defined by SQLModel metadata.

    This is suitable for development. For production, consider using
    Alembic migrations instead.
    """
    # Import all entity models so SQLModel registers their table metadata
    from model.entity.account import Account  # noqa: F401
    from model.entity.article import Article  # noqa: F401
    from model.entity.refresh_token import RefreshToken  # noqa: F401
    from model.entity.user import User  # noqa: F401
    from model.entity.user_word_set_cross_ref import UserWordSetCrossRef  # noqa: F401
    from model.entity.word import Word  # noqa: F401
    from model.entity.word_set import WordSet  # noqa: F401
    from model.entity.word_set_cross_ref import WordSetCrossRef  # noqa: F401
    from model.entity.word_srs import WordSrs  # noqa: F401
    from model.entity.user_grammar_progress import UserGrammarProgress  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency that yields a database session."""
    with Session(engine) as session:
        yield session
