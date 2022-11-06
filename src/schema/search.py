from pydantic import BaseModel


class SearchResponse(BaseModel):
    results: dict
