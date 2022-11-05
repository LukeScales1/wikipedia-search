from bs4 import BeautifulSoup


def parse_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    divs = soup.find_all('div')
    main_text = divs[0].getText()
    return main_text
