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


class ListTypes(Enum):
    RANDOM = "random"


class DefaultParams(BaseModel):
    action: Actions = Actions.QUERY
    data_format: DataFormats = Field(alias="format", default=DataFormats.JSON)

    class Config:
        use_enum_values = True


class ArticleTitlesGet(DefaultParams):
    list_type: ListTypes = Field(alias="list", default=ListTypes.RANDOM)
    limit: int = Field(alias="rnlimit", default=5)
    name_space: int = Field(alias="rnnamespace", default=0)
