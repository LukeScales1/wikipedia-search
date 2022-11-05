import requests
from fastapi import FastAPI

from schema.parser import ParsedText, ProcessedText
from schema.scraper import (
    ArticleTitlesGet, ArticleTitlesGetResponse, ContentGet, ContentGetResponse,
    parse_article_html_or_none,
)
from services.nlp import lemmatize, set_up_nltk
from services.parser import parse_text_from_html
from services.scraper import get_random_articles, get_article_content

set_up_nltk()
app = FastAPI()
s = requests.Session()
text_processor = lemmatize


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
async def get_parsed_content(page_name: str):
    content = get_article_content(s, ContentGet(page=page_name))
    html = parse_article_html_or_none(content["data"])
    text = parse_text_from_html(html)
    return text_processor(text)
