from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_get_articles():
    response = client.get("/articles")
    assert response.status_code == 200
    assert len(response.json()) == 5


def test_get_content():
    response = client.get("/content/Linus_Torvalds")
    assert response.status_code == 200
    assert "<div class=" in response.json()["data"]


def test_parse_content():
    response = client.get("/parse/Linus_Torvalds")
    assert response.status_code == 200
    assert "Creator and lead developer of the Linux kernel" in response.json()["text"]


def test_process_content():
    response = client.get("/process/Linus_Torvalds")
    assert response.status_code == 200
    assert response.json()[0] == "creator"

