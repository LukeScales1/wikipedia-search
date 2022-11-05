import requests
from fastapi import FastAPI

from schema.scraper import ArticleTitlesGet, ArticleTitlesGetResponse, ContentGet, ContentGetResponse
from services.scraper import fetch_random_articles, scrape_article_content

app = FastAPI()
s = requests.Session()


@app.get("/articles", response_model=ArticleTitlesGetResponse)
async def get_articles():
    return fetch_random_articles(s, ArticleTitlesGet())


@app.get("/content/{page_name}", response_model=ContentGetResponse)
async def get_content(page_name: str):
    return scrape_article_content(s, ContentGet(page=page_name))
