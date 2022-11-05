import requests
from fastapi import FastAPI

from schema.scraper import ArticleTitlesGet, ArticleTitlesGetResponse
from services.scraper import fetch_random_articles

app = FastAPI()
s = requests.Session()


@app.get("/articles", response_model=ArticleTitlesGetResponse)
async def get_articles():
    return fetch_random_articles(s, ArticleTitlesGet())
