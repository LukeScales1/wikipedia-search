import logging
import time
from typing import Optional, Union

import requests
from fastapi import FastAPI, Query
from requests import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import wikipedia.service as article_service
from index.indexer import create_or_update_inverted_index, rank_documents
from index.nlp import lemmatize, set_up_nltk
from index.schema import SearchResponse
from wikipedia.client import (get_article_content, get_article_list, get_parsed_text,
                              parse_article_html_or_none, parse_text_from_html)
from wikipedia.models import Article
from wikipedia.parser import parse_article_titles
from wikipedia.schema import (ArticleSchema, ArticleTitlesGet, ArticleTitlesGetResponse,
                              ContentGet, ContentGetResponse, ParsedText, ProcessedText)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig()

set_up_nltk()
app = FastAPI()
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
    articles = get_article_list(session, params)
    return [
        ArticleSchema(
            title=entry["title"],
            tokenized_content=text_processor(
                get_parsed_text(session, page_name=entry["title"])
            ),
        )
        for entry in parse_article_titles(articles)
    ]


def _index_documents(session: Session, articles: Optional[list[ArticleSchema]] = None):
    logger.info("Indexing documents...")
    start_time = time.time()
    fetch_time = None

    articles = articles or article_service.get_all_articles(session=db_session)

    if not articles:
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


@app.get("/articles", response_model=ArticleTitlesGetResponse)
async def get_articles():
    """ Get some fresh, random articles from Wikipedia. """
    return get_article_list(s, ArticleTitlesGet())


@app.get("/content/{page_name}", response_model=ContentGetResponse)
async def get_content(page_name: str):
    """ Get the raw HTML content of a Wikipedia article. """
    return get_article_content(s, ContentGet(page=page_name))


@app.get("/parse/{page_name}", response_model=ParsedText)
async def get_parsed_content(page_name: str):
    """ Get the parsed text of a Wikipedia article. """
    content = get_article_content(s, ContentGet(page=page_name))
    html = parse_article_html_or_none(content["data"])
    return {"text": parse_text_from_html(html)}


@app.get("/process/{page_name}", response_model=ProcessedText)
async def get_processed_content(page_name: str):
    """ Get the processed text of a Wikipedia article. """
    text = get_parsed_text(s, page_name)
    return text_processor(text)


@app.get("/search", response_model=SearchResponse)
async def get_results(query: Union[str, None] = Query(default=None)):
    """ Search for articles that the app has already indexed from Wikipedia, based on a query string. """
    results = None
    if query:
        query = text_processor(query)
        results = rank_documents(query)

    return {"results": results or {}}
