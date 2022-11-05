"""
    Adapted from MediaWiki API Demos

    MIT License
"""

import requests

from schema.scraper import ArticleTitlesGet, ArticleTitlesGetResponse, ScrapeArticleGet

URL = "https://en.wikipedia.org/w/api.php"

s = requests.Session()


def fetch_random_articles(session, params: ArticleTitlesGet) -> ArticleTitlesGetResponse:

    r = session.get(url=URL, params=params.dict(by_alias=True))
    r.raise_for_status()

    return ArticleTitlesGetResponse(data=r.json())


def scrape_article_content(session, params: ScrapeArticleGet):
    r = session.get(url=URL, params=params.dict(by_alias=True))
    r.raise_for_status()

    return r.json()


if __name__ == "__main__":
    article_titles = fetch_random_articles(session=s, params=ArticleTitlesGet())
    for title in article_titles:
        print(title)
        content = scrape_article_content(s, params=ScrapeArticleGet(page=title))
        print(content["parse"].keys())
        print(content["parse"]["text"].keys())
        print(content["parse"]["text"]["*"])
        break
