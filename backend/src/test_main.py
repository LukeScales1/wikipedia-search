import logging

import pytest
from common.models import Base
from fastapi.testclient import TestClient
from main import _index_documents, app, get_db_session
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker
from wikipedia.schema import ArticleSchema

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """
    Override the `get_db_session` FastAPI app dependency to use a test database session.
    """
    db = None
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        if db:
            db.close()


app.dependency_overrides[get_db_session] = override_get_db

client = TestClient(app)


TEST_ARTICLE = ArticleSchema(
    title="Linus Torvalds",
    tokenized_content=[
        "Linus", "Benedict", "Torvalds", "is", "a", "Finnish", "American", "software", "engineer", "who", "is",
        "the", "creator", "and", "historically", "the", "principal", "developer", "of", "the", "Linux", "kernel",
    ]
)


@pytest.fixture
def article():
    """ Returns a test article DB model. """
    return TEST_ARTICLE.to_db_model()


@pytest.fixture(scope="function")
def add_article(article):
    """
    Add a test article to the database and manages removal after test.
    :param article: test article fixture
    """
    db_session = TestingSessionLocal()
    db_session.add(article)
    db_session.commit()
    logger.info("Added test article to the database.")
    yield
    db_session.delete(article)
    db_session.commit()
    db_session.close()


@pytest.fixture
def index_documents():
    """
    Indexes documents in test session.
    """
    db_session = TestingSessionLocal()
    _index_documents(db_session)
    logger.info("Indexed documents.")
    db_session.close()


def test_get_articles_returns_empty_array_if_no_records():
    """ Test that the get_articles endpoint returns an empty array if there are no records in the database. """
    response = client.get("/articles")
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_get_articles(add_article):
    """ Test that the get_articles endpoint returns the correct number of records.

    In this case, we have only one article added from fixtures.

    :param add_article: fixture to add an article to the database.
    """
    response = client.get("/articles")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == TEST_ARTICLE.title


def test_get_article_parses_tokenized_content_correctly(add_article):
    """ Test that article content is correctly parsed between the database and the API.

    In this case, we have only one article added from fixtures.

    :param add_article: fixture to add an article to the database.
    """
    response = client.get("/articles")
    assert response.status_code == 200
    assert response.json()[0]["tokenized_content"] == TEST_ARTICLE.tokenized_content


def test_get_search_results(add_article, index_documents):
    """ Test that the search endpoint returns the correct results.

    In this case, we have only one article added from fixtures.

    :param add_article: fixture to add an article to the database.
    :param index_documents: fixture to index documents in the database.
    """
    response = client.get("/search?query=creator")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == TEST_ARTICLE.title


def test_get_search_results_empty_response(add_article, index_documents):
    """ Test that the search endpoint returns an empty response if no valid articles are found.

    In this case, we have only one article added from fixtures, but the query is irrelevant to the article.

    :param add_article: fixture to add an article to the database.
    """
    response = client.get("/search?query=football")
    assert response.status_code == 200
    assert len(response.json()) == 0
