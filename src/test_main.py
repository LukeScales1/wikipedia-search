from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_get_articles():
    response = client.get("/articles")
    assert response.status_code == 200
    assert len(response.json()) == 5
