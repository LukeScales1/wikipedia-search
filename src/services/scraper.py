"""
    Adapted from MediaWiki API Demos at
    https://www.mediawiki.org/wiki/API:Random#Python
    &
    https://www.mediawiki.org/wiki/API:Parsing_wikitext#Python

    MIT License
"""

from requests.sessions import Session

from schema.scraper import Article, ArticleTitlesGet, ContentGet, parse_article_titles

URL = "https://en.wikipedia.org/w/api.php"


def get_random_articles(session: Session, params: ArticleTitlesGet) -> dict:

    r = session.get(url=URL, params=params.dict(by_alias=True))
    r.raise_for_status()

    return r.json()


def parse_random_articles(session: Session, params: ArticleTitlesGet) -> list[Article]:
    articles = get_random_articles(session, params)
    return [
        Article(
            title=entry["title"]
        )
        for entry in parse_article_titles(articles)
    ]


def get_article_content(session: Session, params: ContentGet) -> dict:
    r = session.get(url=URL, params=params.dict(by_alias=True))
    r.raise_for_status()

    return {"data": r.json()}
