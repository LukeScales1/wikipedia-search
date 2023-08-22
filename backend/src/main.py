from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from typing import Annotated, Optional, Union

from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.orm import sessionmaker

import wikipedia.service as article_service
from index.indexer import create_or_update_inverted_index, rank_documents
from index.schema import SearchResult
from settings import DB_CONNECTION, NUMBER_OF_ARTICLES, text_processor
from wikipedia.schema import ArticleSchema, ArticleTitlesGet

logger = logging.getLogger(__name__)

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


def _index_documents(db_session: DBSession):
    """ Helper function for indexing documents. """
    logger.info("Indexing documents...")

    articles = article_service.get_articles_as_schema(db_session=db_session)
    if not articles:
        logger.info("No articles in DB. Fetching new articles...")
        articles = article_service.fetch_and_add_articles(
            db_session=db_session,
            params=ArticleTitlesGet(rnlimit=NUMBER_OF_ARTICLES)
        )

    index_start_time = time.time()
    create_or_update_inverted_index(
        articles=articles
    )
    index_stop_time = time.time()

    logger.info(f"Time taken to index articles: {index_stop_time - index_start_time}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs this function when the app starts up.
    :param app:
    """
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

    :param db_session: The database session dependency.
    :param limit: The maximum number of articles to return.
    :param offset: The number of articles to skip.
    """
    return article_service.filter_articles(session=db_session, limit=limit, offset=offset)


@app.post("/articles", response_model=list[ArticleSchema])
async def fetch_new_articles(db_session: Annotated[DBSession, Depends(get_db_session)]):
    """ Get some random articles from Wikipedia, add to the DB, and reindex.

    Returns the new articles.

    :param db_session: The database session dependency.
    """
    new_articles = article_service.fetch_and_add_articles(
        db_session=db_session, params=ArticleTitlesGet(rnlimit=NUMBER_OF_ARTICLES)
    )
    create_or_update_inverted_index(
        articles=new_articles
    )
    return new_articles


@app.get("/search", response_model=list[SearchResult])
async def get_results(query: Union[str, None] = Query(default=None)):
    """ Search for articles that the app has already indexed from Wikipedia, based on a query string.

    :param query: The query string to search for.
    """
    results = []
    if query:
        query = text_processor(query)
        results = rank_documents(query)

    return results
