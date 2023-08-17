# flake8: noqa E402
import os
import sys
import unittest

import pytest
from fastapi.testclient import TestClient

PROJECT_PATH = os.getcwd()
SOURCE_PATH = os.path.join(
    PROJECT_PATH, "src"
)
sys.path.append(SOURCE_PATH)

from src.index.indexer import _reset_index
from src.main import _index_documents, app, s, text_processor
from src.wikipedia.client import get_parsed_text
from src.wikipedia.schema import ArticleSchema

client = TestClient(app)
TEST_SEARCH = "Linus_Torvalds"


@pytest.fixture(scope="class")
def index_documents():
    _reset_index()
    articles = [
        ArticleSchema(
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
        response = client.get("/search?query=creator")
        assert response.status_code == 200
        assert TEST_SEARCH in response.json()["results"].keys()
