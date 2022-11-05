from pydantic import BaseModel


class SearchResponse(BaseModel):
    results: list[str]
