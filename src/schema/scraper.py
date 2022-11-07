from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, validator


class DataFormats(Enum):
    """
    Possible data formats from the Wiki API, as of https://www.mediawiki.org/wiki/API:Data_formats#Output.
    """

    JSON = "json"
    PHP = "php"
    XML = "xml"
    TXT = "txt"
    DBG = "dbg"
    YAML = "yaml"
    WDDX = "wddx"
    DUMP = "dump"
    NONE = "none"


class Actions(Enum):
    """
    Accepted actions for Wiki API. Many more possible actions at https://www.mediawiki.org/wiki/API:Main_page#main.
    """

    PARSE = "parse"
    QUERY = "query"


class ListTypes(Enum):
    RANDOM = "random"


""" 
Request Schema 
"""


class DefaultParams(BaseModel):
    action: Actions = Actions.QUERY
    data_format: DataFormats = Field(alias="format", default=DataFormats.JSON)

    class Config:
        use_enum_values = True


class ArticleTitlesGet(DefaultParams):
    list_type: ListTypes = Field(alias="list", default=ListTypes.RANDOM)
    limit: int = Field(alias="rnlimit", default=5)
    name_space: int = Field(alias="rnnamespace", default=0)


class ContentGet(DefaultParams):
    action = Actions.PARSE
    page: str


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


def parse_article_titles(data: dict):
    query = data.get("query", {})
    return query.get("random")


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


def parse_article_html_or_none(content: dict) -> str | None:
    content = content.get("parse", {})
    text = content.get("text", {})
    return text.get("*")


class ContentGetResponse(BaseModel):
    data: str

    @validator('data', pre=True)
    def validate_text(cls, value: dict):
        data = parse_article_html_or_none(value)

        if not data:
            raise ValueError("No results returned from scrape request!")

        return data
