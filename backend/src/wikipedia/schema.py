from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from common.schema import Actions, DefaultParams
from wikipedia.models import Article


class ListTypes(Enum):
    """
    A number of list types are available for the Wiki API, however we are only using `random` for now. Set up as an
    enum to facilitate any further work. See https://www.mediawiki.org/wiki/API:Lists/All for more.
    """
    RANDOM = "random"


def reformat_tokenized_content(content: str) -> list[str]:
    """ Reformats the string representation of tokenized content into a list of strings.

    Removes any whitespace, braces and quotes, and splits on commas.
    """
    import re
    return re.split(r"[,\s]+", re.sub(r"[\[\]{}']", "", content))


class ArticleSchema(BaseModel, from_attributes=True):
    title: str
    tokenized_content: Optional[list[str]]

    @field_validator('tokenized_content', mode="before")
    def validate_tokenized_content(cls, value: str | list[str] | None):
        """
        Validate the tokenized content of an article. If the value is a string, it is assumed to be a comma-separated
        """
        if not value:
            return None

        if type(value) is str:
            return reformat_tokenized_content(value)

        return value

    def to_db_model(self) -> Article:
        """ Convert an ArticleSchema to a DB model. """
        return Article(
            title=self.title,
            tokenized_content=",".join(self.tokenized_content),
        )


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
