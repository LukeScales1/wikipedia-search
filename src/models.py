"""
DB models for application
"""
from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Article(Base):
    """ A Wikipedia article's tokenized content by title. """
    __tablename__ = "article"

    title = Column(String, primary_key=True)
    tokenized_content = Column(String, nullable=True, default=None)  # can be None if content has not been tokenized yet
