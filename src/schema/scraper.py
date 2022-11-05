from enum import Enum

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


class ScrapeArticleGet(DefaultParams):
    action = Actions.PARSE
    page: str


"""
Response Schema
"""


class Articles(BaseModel):
    title: str


class ArticleIterator:
    def __init__(self, articles: list[Articles]):
        self.articles = articles
        self.current_index = 0

    def __next__(self) -> str:
        if self.current_index >= len(self.articles):
            raise StopIteration

        current_item = self.articles[self.current_index]
        self.current_index += 1

        return current_item.title


class ArticleTitlesGetResponse(BaseModel):
    __root__: list[Articles]

    @validator('__root__', pre=True)
    def validate_data(cls, value: dict):
        query = value.get("query", {})
        random = query.get("random")

        if not random:
            raise ValueError("No results returned from fetch titles request!")

        return random

    def __iter__(self):
        return ArticleIterator(self.__root__)
