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
from services.index import create_or_update_inverted_index, rank_inverted_docs
from services.nlp import lemmatize, set_up_nltk
from services.parser import get_parsed_text, parse_text_from_html
from services.scraper import get_random_articles, get_article_content, parse_random_articles

set_up_nltk()
app = FastAPI()
s = requests.Session()
text_processor = lemmatize
INDEX = Index()
NUMBER_OF_ARTICLES = 5


def _index_documents(session: Session, articles: Optional[list[Article]] = None):
    global INDEX

    if not articles:
        articles = parse_random_articles(session, ArticleTitlesGet(rnlimit=NUMBER_OF_ARTICLES))

    INDEX = create_or_update_inverted_index(
        session=session,
        articles=articles,
        text_processor=text_processor,
        index=INDEX
    )

    # index more articles to ensure that index can be updated
    articles = parse_random_articles(session, ArticleTitlesGet(rnlimit=NUMBER_OF_ARTICLES))
    INDEX = create_or_update_inverted_index(
        session=session,
        articles=articles,
        text_processor=text_processor,
        index=INDEX
    )


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
        results = rank_inverted_docs(q, INDEX)

    return {"results": results or {}}
