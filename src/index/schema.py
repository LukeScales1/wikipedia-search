from pydantic import BaseModel

"""
Response Schema
"""


class SearchResponse(BaseModel):
    results: dict
