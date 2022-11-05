from __future__ import annotations

from pydantic import BaseModel

from services.parser import parse_text_from_html


class ParsedText(BaseModel):
    text: str

    @classmethod
    def from_html(cls, html: str) -> ParsedText:
        return cls(
            text=parse_text_from_html(html)
        )


class ProcessedText(BaseModel):
    __root__: list[str]

