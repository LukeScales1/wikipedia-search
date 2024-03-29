"""
DB service for CRUD operations on Wikipedia Article model.
"""
from __future__ import annotations

import logging
from typing import Sequence

import requests
from sqlalchemy import select
from sqlalchemy.orm import Session

from index.nlp import TextProcessor
from wikipedia.client import get_and_parse_random_articles
from wikipedia.models import Article
from wikipedia.schema import ArticleSchema, ArticleTitlesGet

logger = logging.getLogger(__name__)


def get_article(session: Session, page_name: str) -> Article | None:
    """ Get an article by title.

    :param session: The database session.
    :param page_name: The title of the article.
    """
    query = select(Article).where(Article.c.title == page_name)
    return session.execute(query).first()


def filter_articles(session: Session, limit: int | None = None, offset: int | None = None) -> Sequence[Article]:
    """ Get all articles from the database.

    :param session: The database session.
    :param limit: The (optional) maximum number of articles to return.
    :param offset: The (optional) number of articles to skip.
    """
    query = select(Article)
    if limit:
        query = query.limit(limit)
    if offset:
        query = query.offset(offset)

    return session.scalars(query).all()


def add_article(session: Session, article: Article):
    """ Add an article to the database.

    :param session: The database session.
    :param article: The article to add.
    """
    session.add(article)
    session.commit()


def add_articles_bulk(session: Session, articles: list[Article]):
    """ Add a list of articles to the database.

    :param session: The database session.
    :param articles: The articles to add.
    """
    session.bulk_save_objects(articles)
    session.commit()


def update_article(session: Session, article: Article):
    """ Update an article in the database.

    :param session: The database session.
    :param article: The article to update.
    """
    session.merge(article)
    session.commit()


def delete_article(session: Session, article: Article):
    """ Delete an article from the database.

    :param session: The database session.
    :param article: The article to delete.
    """
    session.delete(article)
    session.commit()


def fetch_and_add_articles(
        db_session: Session,
        params: ArticleTitlesGet,
        text_processor: TextProcessor,
) -> list[ArticleSchema]:
    """
    Fetches articles from Wikipedia and adds them to the database.

    :param db_session: The database session.
    :param params: The parameters to pass to the Wikipedia API.
    :param text_processor: The text processor to use to process the articles.
    """
    with requests.Session() as session:
        articles = get_and_parse_random_articles(session, params, text_processor)
    logger.info(f"{len(articles)} articles fetched!")
    add_articles_bulk(
        session=db_session,
        articles=[
            article_schema.to_db_model()
            for article_schema in articles
        ]
    )
    return articles


def get_articles_as_schema(db_session: Session, **filter_kwargs) -> list[ArticleSchema]:
    """ Get articles from the database as ArticleSchema objects.

    :param db_session: The database session.
    :param filter_kwargs: Keyword arguments to filter the articles by.
    """
    db_articles = filter_articles(session=db_session, **filter_kwargs)
    return [
        ArticleSchema.model_validate(article)
        for article in db_articles
    ]
