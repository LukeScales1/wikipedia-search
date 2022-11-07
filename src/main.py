import logging
import multiprocessing
import time
from typing import Optional, Union

import requests
from fastapi import FastAPI, Query
from requests import Session

from schema.index import Index
from schema.parser import ParsedText, ProcessedText
from schema.scraper import (
    Article, ArticleTitlesGet, ArticleTitlesGetResponse, ContentGet, ContentGetResponse,
    parse_article_html_or_none,
)
from schema.search import SearchResponse
from services.index import create_or_update_inverted_index, rank_documents
from services.nlp import lemmatize, set_up_nltk
from services.parser import get_parsed_text, parse_text_from_html, parse_random_articles
from services.scraper import get_random_articles, get_article_content

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig()

set_up_nltk()
app = FastAPI()
s = requests.Session()
text_processor = lemmatize
INDEX = Index()
NUMBER_OF_ARTICLES = 200
ARTICLE_CHUNK_SIZE = 10


def _fetch_and_process_articles(session: Session):
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    processes = [
        pool.apply_async(
            parse_random_articles,
            args=(session, ArticleTitlesGet(rnlimit=ARTICLE_CHUNK_SIZE), text_processor,)
        ) for x in range(ARTICLE_CHUNK_SIZE, NUMBER_OF_ARTICLES+ARTICLE_CHUNK_SIZE, ARTICLE_CHUNK_SIZE)]
    return [article for p in processes for article in p.get()]


def _reset_index():
    global INDEX
    INDEX = Index()


def _index_documents(session: Session, articles: Optional[list[Article]] = None):
    global INDEX

    start_time = time.time()
    fetch_time = None

    if not articles:
        articles = _fetch_and_process_articles(session)
        fetch_time = time.time()

    index_start_time = time.time()
    INDEX = create_or_update_inverted_index(
        articles=articles,
        index=INDEX
    )
    index_stop_time = time.time()
    if fetch_time:
        logger.info(f"Time taken to fetch and tokenize articles: {fetch_time - start_time}")

    logger.info(f"Time taken to index articles: {index_stop_time - index_start_time}")


_index_documents(s)


@app.get("/articles", response_model=ArticleTitlesGetResponse)
async def get_articles():
    return get_random_articles(s, ArticleTitlesGet())


@app.get("/content/{page_name}", response_model=ContentGetResponse)
async def get_content(page_name: str):
    return get_article_content(s, ContentGet(page=page_name))


@app.get("/parse/{page_name}", response_model=ParsedText)
async def get_parsed_content(page_name: str):
    content = get_article_content(s, ContentGet(page=page_name))
    html = parse_article_html_or_none(content["data"])
    return {"text": parse_text_from_html(html)}


@app.get("/process/{page_name}", response_model=ProcessedText)
async def get_processed_content(page_name: str):
    text = get_parsed_text(s, page_name)
    return text_processor(text)


@app.get("/search/", response_model=SearchResponse)
async def get_results(q: Union[str, None] = Query(default=None)):
    results = None
    if q:
        q = text_processor(q)
        results = rank_documents(q, INDEX)

    return {"results": results or {}}
