from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, validator

from schema.common import DefaultParams
from services.parser import parse_article_html_or_none, parse_article_titles


class ListTypes(Enum):
    """
    A number of list types are available for the Wiki API, however we are only using `random` for now. Set up as an
    enum to facilitate any further work. See https://www.mediawiki.org/wiki/API:Lists/All for more.
    """
    RANDOM = "random"


"""
Request Schema
"""


class ArticleTitlesGet(DefaultParams):
    list_type: ListTypes = Field(alias="list", default=ListTypes.RANDOM)
    limit: int = Field(alias="rnlimit", default=5)
    name_space: int = Field(alias="rnnamespace", default=0)


"""
Response Schema
"""


class Article(BaseModel):
    title: str
    tokenized_content: Optional[list[str]]


class ArticleIterator:
    def __init__(self, articles: list[Article]):
        self.articles = articles
        self.current_index = 0

    def __next__(self) -> str:
        if self.current_index >= len(self.articles):
            raise StopIteration

        current_item = self.articles[self.current_index]
        self.current_index += 1

        return current_item.title


class ArticleTitlesGetResponse(BaseModel):
    __root__: list[Article]

    @validator('__root__', pre=True)
    def validate_data(cls, value: dict):
        data = parse_article_titles(value)

        if not data:
            raise ValueError("No results returned from fetch titles request!")

        return data

    def __iter__(self):
        return ArticleIterator(self.__root__)


class ContentGetResponse(BaseModel):
    data: str

    @validator('data', pre=True)
    def validate_text(cls, value: dict):
        data = parse_article_html_or_none(value)

        if not data:
            raise ValueError("No results returned from scrape request!")

        return data
