from typing import Optional

from sqlmodel import Field, SQLModel


class Article(SQLModel, table=True):
    """Article / reading content mapped to 'article' table."""

    __tablename__ = "article"

    article_id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field()
    content: str = Field()
    description: str = Field(default="")
    category: str = Field(default="")
    level: str = Field(default="")
    read_time: str = Field(default="")
    image: str = Field(default="")
    author: str = Field(default="")
