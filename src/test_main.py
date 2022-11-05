from fastapi.testclient import TestClient

from main import app

client = TestClient(app)
TEST_SEARCH = "Linus_Torvalds"


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


def test_search():
    response = client.get("/search/?q=test%20this%20brilliant%20thing")
    assert response.status_code == 200
    assert response.json() == {"results": ["test", "brilliant", "thing"]}

