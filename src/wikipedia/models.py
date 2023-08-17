"""
DB models for application
"""
from __future__ import annotations

from sqlalchemy import Column, String

from common.models import Base


class Article(Base):
    """ A Wikipedia article's tokenized content by title. """
    __tablename__ = "article"

    title = Column(String, primary_key=True)
    tokenized_content = Column(String, nullable=True, default=None)  # can be None if content has not been tokenized yet

    @classmethod
    def from_dict(cls, article_dict: dict[str, str]) -> Article:
        """ Create an Article from a dictionary. """
        return cls(
            title=article_dict["title"],
            tokenized_content=article_dict["tokenized_content"],
        )
