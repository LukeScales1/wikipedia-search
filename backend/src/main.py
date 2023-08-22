from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from typing import Annotated, Optional, Union

import requests
import wikipedia.service as article_service
from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from index.indexer import create_or_update_inverted_index, rank_documents
from index.nlp import lemmatize, set_up_nltk
from index.schema import SearchResult
from requests import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.orm import sessionmaker
from wikipedia.client import fetch_article_list, fetch_parsed_text
from wikipedia.models import Article
from wikipedia.parser import parse_article_titles
from wikipedia.schema import ArticleSchema, ArticleTitlesGet

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig()

set_up_nltk()

text_processor = lemmatize

NUMBER_OF_ARTICLES = 10


DB_CONNECTION = "postgresql+psycopg2://postgres:password@db:5432/wiki-search"
engine = create_engine(DB_CONNECTION)
db_session_maker = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def get_db_session():
    """
    Get a managed database session from the database connection pool.
    """
    db_session = None
    try:
        db_session = db_session_maker()
        yield db_session
    finally:
        if db_session:
            db_session.close()

DbSessionDeps = Annotated[Optional[DBSession], Depends(get_db_session)]


def get_and_parse_random_articles(
        session: Session,
        params: ArticleTitlesGet,
) -> list[ArticleSchema]:
    """ Helper function for fetching and processing a list of random articles. """
    articles = fetch_article_list(session, params)
    return [
        ArticleSchema(
            title=entry["title"],
            tokenized_content=text_processor(
                fetch_parsed_text(session, page_name=entry["title"])
            ),
        )
        for entry in parse_article_titles(articles)
    ]


def _index_documents(db_session: DBSession):
    """ Helper function for indexing documents. """
    logger.info("Indexing documents...")
    start_time = time.time()
    fetch_time = None

    db_articles = article_service.filter_articles(session=db_session)

    if not db_articles:
        logger.info("No articles found in database. Fetching some from Wikipedia...")
        with requests.Session() as session:
            articles = get_and_parse_random_articles(session, ArticleTitlesGet(rnlimit=NUMBER_OF_ARTICLES))
        fetch_time = time.time()
        logger.info(f"{len(articles)} articles fetched!")
        article_service.add_articles_bulk(
            session=db_session,
            articles=[
                Article.from_dict(article_schema.dict())
                for article_schema in articles
            ]
        )
    else:
        articles = [
            ArticleSchema.from_orm(article)
            for article in db_articles
        ]
        logger.info(f"{len(articles)} articles found in database.")

    index_start_time = time.time()
    create_or_update_inverted_index(
        articles=articles
    )
    index_stop_time = time.time()
    if fetch_time:
        logger.info(f"Time taken to fetch and tokenize articles: {fetch_time - start_time}")

    logger.info(f"Time taken to index articles: {index_stop_time - index_start_time}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_session = db_session_maker()
    _index_documents(db_session)
    db_session.close()
    yield


app = FastAPI(lifespan=lifespan)
origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def index():
    """ Landing page for the app. """
    return {"message": "Welcome!! Please check out the docs at localhost:8000/docs!"}


@app.get("/articles", response_model=list[ArticleSchema])
async def get_articles(
        db_session: DbSessionDeps,
        limit: int = Query(default=0, gt=0, le=100),
        offset: int = Query(default=0, ge=0),
):
    """ Get articles from the DB, with optional limit and offset.

    Defaults to all articles in the DB if no limit provided. Offset can be used without a limit.

    :param db_session: The database session.
    :param limit: The maximum number of articles to return.
    :param offset: The number of articles to skip.
    """
    return article_service.filter_articles(session=db_session, limit=limit, offset=offset)


@app.post("/articles", response_model=list[ArticleSchema])
async def fetch_new_articles(db_session: Annotated[DBSession, Depends(get_db_session)]):
    """ Get some random articles from Wikipedia, add to the DB, and reindex. """
    with requests.Session() as session:
        new_articles = get_and_parse_random_articles(session, ArticleTitlesGet(rnlimit=NUMBER_OF_ARTICLES))
    article_service.add_articles_bulk(
        session=db_session,
        articles=[
            article_schema.to_db_model()
            for article_schema in new_articles
        ]
    )
    create_or_update_inverted_index(
        articles=new_articles
    )
    return new_articles


@app.get("/search", response_model=list[SearchResult])
async def get_results(query: Union[str, None] = Query(default=None)):
    """ Search for articles that the app has already indexed from Wikipedia, based on a query string. """
    results = []
    if query:
        query = text_processor(query)
        results = rank_documents(query)

    return results
