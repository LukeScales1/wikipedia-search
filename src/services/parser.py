from bs4 import BeautifulSoup
from requests import Session

from schema.scraper import ContentGet, parse_article_html_or_none
from services.scraper import get_article_content


def parse_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    divs = soup.find_all('div')
    main_text = divs[0].getText()
    return main_text


def get_parsed_text(session: Session, page_name: str):
    content = get_article_content(session, ContentGet(page=page_name))
    html = parse_article_html_or_none(content["data"])
    return parse_text_from_html(html)
