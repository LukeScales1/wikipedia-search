from typing import Callable

from bs4 import BeautifulSoup
from requests import Session

from schema.scraper import Article, ArticleTitlesGet, ContentGet, parse_article_html_or_none, parse_article_titles
from services.scraper import get_article_content, get_random_articles


def parse_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    divs = soup.find_all('div')
    main_text = divs[0].getText()
    return main_text


def get_parsed_text(session: Session, page_name: str):
    content = get_article_content(session, ContentGet(page=page_name))
    html = parse_article_html_or_none(content["data"])
    return parse_text_from_html(html)


def parse_random_articles(
        session: Session,
        params: ArticleTitlesGet,
        text_processor: Callable[[str], list[str]]) -> list[Article]:
    articles = get_random_articles(session, params)
    return [
        Article(
            title=entry["title"],
            tokenized_content=text_processor(
                get_parsed_text(session, page_name=entry["title"])
            ),
        )
        for entry in parse_article_titles(articles)
    ]