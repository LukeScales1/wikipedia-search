"""
    Adapted from MediaWiki API Demos at
    https://www.mediawiki.org/wiki/API:Random#Python
    &
    https://www.mediawiki.org/wiki/API:Parsing_wikitext#Python

    MIT License
"""
from __future__ import annotations

from requests.sessions import Session

from settings import text_processor
from wikipedia.parser import parse_article_html_or_none, parse_article_titles, parse_text_from_html
from wikipedia.schema import ArticleSchema, ArticleTitlesGet, ContentGet

URL = "https://en.wikipedia.org/w/api.php"


def fetch_article_list(session: Session, params: ArticleTitlesGet) -> dict:
    """ Get a list of articles from Wikipedia.

    Check the API docs for more info. https://www.mediawiki.org/wiki/API:Lists/All
    """
    r = session.get(url=URL, params=params.model_dump(by_alias=True, mode="json"))
    r.raise_for_status()

    return r.json()


def fetch_article_content(session: Session, params: ContentGet) -> dict:
    """ Get the content of an article from Wikipedia. """
    r = session.get(url=URL, params=params.model_dump(by_alias=True, mode="json"))
    r.raise_for_status()

    return {"data": r.json()}


def fetch_parsed_text(session: Session, page_name: str):
    """ Helper function for fetching an article's content and then parsing the main text. """
    content = fetch_article_content(session, ContentGet(page=page_name))
    html = parse_article_html_or_none(content["data"])
    return parse_text_from_html(html)


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
