from __future__ import annotations

from enum import Enum
from typing import Optional

from common.schema import Actions, DefaultParams
from pydantic import BaseModel, Field, validator
from wikipedia.client import parse_article_html_or_none, parse_text_from_html


class ListTypes(Enum):
    """
    A number of list types are available for the Wiki API, however we are only using `random` for now. Set up as an
    enum to facilitate any further work. See https://www.mediawiki.org/wiki/API:Lists/All for more.
    """
    RANDOM = "random"


class ArticleSchema(BaseModel):
    title: str
    tokenized_content: Optional[list[str]]

    @validator('tokenized_content', pre=True)
    def validate_tokenized_content(cls, value: str | list[str] | None):
        """
        Validate the tokenized content of an article. If the value is a string, it is assumed to be a comma-separated
        """
        if not value:
            return None

        if type(value) is str:
            return value.replace("{", "").replace("}", "").split(",")

        return value

    class Config:
        orm_mode = True


class ParsedText(BaseModel):
    text: str

    @classmethod
    def from_html(cls, html: str) -> ParsedText:
        return cls(
            text=parse_text_from_html(html)
        )


class ProcessedText(BaseModel):
    __root__: list[str]


"""
Request Schema
"""


class ArticleTitlesGet(DefaultParams):
    """ Schema for fetching a list of articles. """
    list_type: ListTypes = Field(alias="list", default=ListTypes.RANDOM)
    limit: int = Field(alias="rnlimit", default=5)
    name_space: int = Field(alias="rnnamespace", default=0)


class ContentGet(DefaultParams):
    """ Schema for fetching the content of an article. """
    action: Actions = Actions.PARSE
    page: str


"""
Response Schema
"""


class ArticlesResponse(BaseModel):
    __root__: list[ArticleSchema]


class ContentGetResponse(BaseModel):
    data: str

    @validator('data', pre=True)
    def validate_text(cls, value: dict):
        data = parse_article_html_or_none(value)

        if not data:
            raise ValueError("No results returned from scrape request!")

        return data
