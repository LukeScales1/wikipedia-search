"""
DB service for CRUD operations on Wikipedia Article model.
"""
from __future__ import annotations

from typing import Type

from sqlalchemy.orm import Session
from wikipedia.models import Article


def get_article(session: Session, page_name: str) -> Article | None:
    """ Get an article by title. """
    return session.query(Article).filter(Article.title == page_name).first()


def get_all_articles(session: Session) -> list[Type[Article]]:
    """ Get all articles from the database. """
    return session.query(Article).all()


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
