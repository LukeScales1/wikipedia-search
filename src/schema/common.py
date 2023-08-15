""" Contains common schema definitions used by other schemas and services. """
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


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


class DefaultParams(BaseModel):
    action: Actions = Actions.QUERY
    data_format: DataFormats = Field(alias="format", default=DataFormats.JSON)

    class Config:
        use_enum_values = True


class ContentGet(DefaultParams):
    """ Schema for fetching the content of an article. Reused in scraper and parser. """
    action: Actions = Actions.PARSE
    page: str
