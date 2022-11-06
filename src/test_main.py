from unittest import mock

from fastapi.testclient import TestClient

from main import _index_documents, app, s

client = TestClient(app)
TEST_SEARCH = "Linus_Torvalds"


def index_documents():
    _index_documents(s)


def mock_random_article_response(*args, **kwargs) -> dict:
    return {
        "query": {
            "random": [
                {"title": TEST_SEARCH}
            ]
        }
    }


def test_get_articles():
    response = client.get("/articles")
    assert response.status_code == 200
    assert len(response.json()) == 5


def test_get_content():
    response = client.get(f"/content/{TEST_SEARCH}")
    assert response.status_code == 200
    assert "<div class=" in response.json()["data"]


def test_parse_content():
    response = client.get(f"/parse/{TEST_SEARCH}")
    assert response.status_code == 200
    assert "Creator and lead developer of the Linux kernel" in response.json()["text"]


def test_process_content():
    response = client.get(f"/process/{TEST_SEARCH}")
    assert response.status_code == 200
    assert response.json()[0] == "creator"


@mock.patch('services.scraper.get_random_articles', mock_random_article_response)
def test_search():
    index_documents()
    response = client.get("/search/?q=creator")
    assert response.status_code == 200
    assert response.json() == {"results": {TEST_SEARCH: -0.8239592165010823}}
