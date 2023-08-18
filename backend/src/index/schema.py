from pydantic import BaseModel


class SearchResult(BaseModel):
    title: str
    ranking: float


class SearchResponse(BaseModel):
    __root__: list[SearchResult]
