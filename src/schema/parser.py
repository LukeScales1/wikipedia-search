from __future__ import annotations

from pydantic import BaseModel


TEST_TEXT = "test+text"


class ParsedText(BaseModel):
    text: str

    @classmethod
    def from_html(cls, html: str) -> ParsedText:
        return cls(
            text=TEST_TEXT
        )
