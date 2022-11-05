"""
    Adapted from MediaWiki API Demos at
    https://www.mediawiki.org/wiki/API:Random#Python
    &
    https://www.mediawiki.org/wiki/API:Parsing_wikitext#Python

    MIT License
"""

import requests

from schema.scraper import ArticleTitlesGet, ArticleTitlesGetResponse, ScrapeArticleGet

URL = "https://en.wikipedia.org/w/api.php"

s = requests.Session()


def fetch_random_articles(session, params: ArticleTitlesGet) -> dict:

    r = session.get(url=URL, params=params.dict(by_alias=True))
    r.raise_for_status()

    return r.json()


def scrape_article_content(session, params: ScrapeArticleGet) -> dict:
    r = session.get(url=URL, params=params.dict(by_alias=True))
    r.raise_for_status()

    return r.json()

