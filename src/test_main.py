from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_get_articles():
    response = client.get("/articles")
    assert response.status_code == 200
    assert len(response.json()) == 5


def test_get_content():
    response = client.get("/content/Fred%20Pincus")  # random request
    assert response.status_code == 200
    assert "<div class=" in response.json()["data"]


def test_parse_content():
    response = client.get("/parse/Fred%20Pincus")  # random request
    assert response.status_code == 200
    assert "\n\nFred L. Pincus" in response.json()["text"]

