"""
DB service for CRUD operations on Wikipedia Article model.
"""
from __future__ import annotations

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session
from wikipedia.models import Article


def get_article(session: Session, page_name: str) -> Article | None:
    """ Get an article by title. """
    query = select(Article).where(Article.c.title == page_name)
    return session.execute(query).first()


def filter_articles(session: Session, limit: int | None = None, offset: int | None = None) -> Sequence[Article]:
    """ Get all articles from the database. """
    query = select(Article)
    if limit:
        query = query.limit(limit)
    if offset:
        query = query.offset(offset)

    return session.scalars(query).all()


def add_article(session: Session, article: Article):
    """ Add an article to the database. """
    session.add(article)
    session.commit()


def add_articles_bulk(session: Session, articles: list[Article]):
    """ Add a list of articles to the database. """
    session.bulk_save_objects(articles)
    session.commit()


def update_article(session: Session, article: Article):
    """ Update an article in the database. """
    session.merge(article)
    session.commit()


def delete_article(session: Session, article: Article):
    """ Delete an article from the database. """
    session.delete(article)
    session.commit()
