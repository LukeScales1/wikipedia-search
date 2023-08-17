"""
    Adapted from MediaWiki API Demos at
    https://www.mediawiki.org/wiki/API:Random#Python
    &
    https://www.mediawiki.org/wiki/API:Parsing_wikitext#Python

    MIT License
"""
from __future__ import annotations

from requests.sessions import Session
from wikipedia.parser import parse_article_html_or_none, parse_text_from_html
from wikipedia.schema import ArticleTitlesGet, ContentGet

URL = "https://en.wikipedia.org/w/api.php"


def get_article_list(session: Session, params: ArticleTitlesGet) -> dict:
    """ Get a list of articles from Wikipedia.

    Check the API docs for more info. https://www.mediawiki.org/wiki/API:Lists/All
    """
    r = session.get(url=URL, params=params.dict(by_alias=True))
    r.raise_for_status()

    return r.json()


def get_article_content(session: Session, params: ContentGet) -> dict:
    """ Get the content of an article from Wikipedia. """
    r = session.get(url=URL, params=params.dict(by_alias=True))
    r.raise_for_status()

    return {"data": r.json()}


def get_parsed_text(session: Session, page_name: str):
    """ Helper function for fetching an article's content and then parsing the main text. """
    content = get_article_content(session, ContentGet(page=page_name))
    html = parse_article_html_or_none(content["data"])
    return parse_text_from_html(html)
