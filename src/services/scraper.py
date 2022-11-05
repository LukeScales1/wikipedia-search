"""
    Adapted from MediaWiki API Demos

    MIT License
"""

import requests

from schema.scraper import ArticleTitlesGet

URL = "https://en.wikipedia.org/w/api.php"

s = requests.Session()


def fetch_random_articles(session, params: ArticleTitlesGet) -> dict:

    r = session.get(url=URL, params=params.dict(by_alias=True))
    r.raise_for_status()

    return r.json()


if __name__ == "__main__":
    data = fetch_random_articles(s, params=ArticleTitlesGet())
    for entry in data["query"]["random"]:
        print(entry["title"])
