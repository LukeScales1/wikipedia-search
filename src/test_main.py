import unittest

import pytest
from fastapi.testclient import TestClient

from main import _index_documents, _reset_index, app, s, text_processor
from schema.scraper import Article
from services.scraper import get_parsed_text

client = TestClient(app)
TEST_SEARCH = "Linus_Torvalds"


@pytest.fixture(scope="class")
def index_documents():
    _reset_index()
    articles = [
        Article(
            title=TEST_SEARCH,
            tokenized_content=text_processor(
                get_parsed_text(s, page_name=TEST_SEARCH)
            )
        )
    ]
    _index_documents(s, articles)


def mock_random_article_response(*args, **kwargs) -> dict:
    return {
        "query": {
            "random": [
                {"title": TEST_SEARCH}
            ]
        }
    }


@pytest.mark.usefixtures("index_documents")
class TestWiki(unittest.TestCase):
    def test_get_articles(self):
        response = client.get("/articles")
        assert response.status_code == 200
        assert len(response.json()) == 5

    def test_get_content(self):
        response = client.get(f"/content/{TEST_SEARCH}")
        assert response.status_code == 200
        assert "<div class=" in response.json()["data"]

    def test_parse_content(self):
        response = client.get(f"/parse/{TEST_SEARCH}")
        assert response.status_code == 200
        assert "Creator and lead developer of the Linux kernel" in response.json()["text"]

    def test_process_content(self):
        response = client.get(f"/process/{TEST_SEARCH}")
        assert response.status_code == 200
        assert response.json()[0] == "creator"

    def test_search(self):
        response = client.get("/search/?q=creator")
        assert response.status_code == 200
        assert response.json() == {"results": {TEST_SEARCH: -0.8239592165010823}}
