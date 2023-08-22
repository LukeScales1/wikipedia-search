from pydantic import BaseModel


class SearchResult(BaseModel):
    title: str
    ranking: float
