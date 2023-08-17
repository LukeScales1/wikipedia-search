from __future__ import annotations

from bs4 import BeautifulSoup


def parse_article_titles(data: dict):
    """ Helper function for parsing the titles of articles from a response. """
    query = data.get("query", {})
    return query.get("random")


def parse_article_html_or_none(content: dict) -> str | None:
    """ Helper function for parsing the HTML of an article from a response. """
    content = content.get("parse", {})
    text = content.get("text", {})
    return text.get("*")


def parse_text_from_html(html: str) -> str:
    """ Parse the main text from the HTML of a Wikipedia article. """
    soup = BeautifulSoup(html, 'html.parser')
    divs = soup.find_all('div')
    main_text = divs[0].getText()
    return main_text
