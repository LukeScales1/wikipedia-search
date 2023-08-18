from __future__ import annotations

import logging
import time
from typing import Union

import requests
import wikipedia.service as article_service
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from index.indexer import create_or_update_inverted_index, rank_documents
from index.nlp import lemmatize, set_up_nltk
from index.schema import SearchResponse
from requests import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from wikipedia.client import (fetch_article_content, fetch_article_list, fetch_parsed_text,
                              parse_article_html_or_none, parse_text_from_html)
from wikipedia.models import Article
from wikipedia.parser import parse_article_titles
from wikipedia.schema import (ArticleSchema, ArticlesResponse, ArticleTitlesGet,
                              ContentGet, ContentGetResponse, ParsedText, ProcessedText)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig()

app = FastAPI()

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

set_up_nltk()

s = requests.Session()
text_processor = lemmatize

NUMBER_OF_ARTICLES = 10


DB_CONNECTION = "postgresql+psycopg2://postgres:password@db:5432"

engine = create_engine(DB_CONNECTION)

DbSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = DbSession()


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


def _index_documents(session: Session):
    logger.info("Indexing documents...")
    start_time = time.time()
    fetch_time = None

    db_articles = article_service.filter_articles(session=db_session)

    if not db_articles:
        logger.info("No articles found in database. Fetching some from Wikipedia...")
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


_index_documents(s)


@app.get("/")
async def index():
    """ Landing page for the app. """
    return {"message": "Welcome!! Please check out the docs at localhost:8000/docs!"}


@app.get("/articles", response_model=ArticlesResponse)
async def get_articles(limit: int = Query(default=0, gt=0, le=100), offset: int = Query(default=0, ge=0)):
    """ Get articles from the DB, with optional limit and offset.

    Defaults to all articles in the DB if no limit provided. Offset can be used without a limit.

    :param limit: The maximum number of articles to return.
    :param offset: The number of articles to skip.
    :raises HTTPException: (404) If no articles are found.
    """
    articles = article_service.filter_articles(session=db_session, limit=limit, offset=offset)
    if not articles:
        raise HTTPException(status_code=404, detail="No articles found!")
    return articles


@app.post("/articles", response_model=ArticlesResponse)
async def fetch_new_articles():
    """ Get some random articles from Wikipedia, add to the DB, and reindex. """
    new_articles = get_and_parse_random_articles(s, ArticleTitlesGet(rnlimit=NUMBER_OF_ARTICLES))
    article_service.add_articles_bulk(
        session=db_session,
        articles=[
            Article.from_dict(article_schema.dict())
            for article_schema in new_articles
        ]
    )
    create_or_update_inverted_index(
        articles=new_articles
    )
    return new_articles


@app.get("/content/{page_name}", response_model=ContentGetResponse)
async def get_content(page_name: str):
    """ Get the raw HTML content of a Wikipedia article. """
    return fetch_article_content(s, ContentGet(page=page_name))


@app.get("/parse/{page_name}", response_model=ParsedText)
async def get_parsed_content(page_name: str):
    """ Get the parsed text of a Wikipedia article. """
    content = fetch_article_content(s, ContentGet(page=page_name))
    html = parse_article_html_or_none(content["data"])
    return {"text": parse_text_from_html(html)}


@app.get("/process/{page_name}", response_model=ProcessedText)
async def get_processed_content(page_name: str):
    """ Get the processed text of a Wikipedia article. """
    text = fetch_parsed_text(s, page_name)
    return text_processor(text)


@app.get("/search", response_model=SearchResponse)
async def get_results(query: Union[str, None] = Query(default=None)):
    """ Search for articles that the app has already indexed from Wikipedia, based on a query string. """
    results = None
    if query:
        query = text_processor(query)
        results = rank_documents(query)

    return {"results": results or {}}
