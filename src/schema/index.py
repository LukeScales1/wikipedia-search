from __future__ import annotations

from collections import Counter, defaultdict
from functools import cached_property
from typing import Iterable

from pydantic import BaseModel


def _reset_cached_properties(object_instance, properties: Iterable[str]):
    """ To be used if the index is ever updated with more articles after instantiation and use. """
    for prop in properties:
        if prop in object_instance.__dict__:
            del object_instance.__dict__[prop]


class DocumentTermInfo(BaseModel):
    """ Contains information about the frequency of one specific term in a document, plus the document's length.

    This is a payload used when ranking a matching document when looking up a search term.
    """
    term_frequency: int = 0
    document_length: int = 0


class TermData(BaseModel):
    document_index: defaultdict[str, DocumentTermInfo] = defaultdict()
    corpus_term_frequency: int = 0

    class Config:
        arbitrary_types_allowed = True
        keep_untouched = (cached_property,)

    @cached_property
    def documents_containing_term(self) -> list[str]:
        return list(self.document_index.keys())

    @cached_property
    def number_of_documents_containing_term(self) -> int:
        return len(self.documents_containing_term)

    def get_document_info(self, document_id: str) -> DocumentTermInfo:
        return self.document_index[document_id]

    def add_document_info(self, document_id: str, term_frequency: int, document_length: int) -> None:
        self.document_index[document_id] = DocumentTermInfo(
            term_frequency=term_frequency,
            document_length=document_length
        )

    def reset_cached_properties(self):
        _reset_cached_properties(
            self,
            properties=(
                "documents_containing_term",
                "number_of_documents_containing_term"
            )
        )


class Index(BaseModel):
    terms: defaultdict[str, TermData] = defaultdict(TermData)
    number_of_documents: int = 0
    document_lengths: list[int] = []

    class Config:
        arbitrary_types_allowed = True
        keep_untouched = (cached_property,)

    @cached_property
    def corpus_size(self) -> int:
        return sum(self.document_lengths)

    @cached_property
    def average_document_length(self) -> float:
        return self.corpus_size / self.number_of_documents

    def get_term_data(self, search_term: str) -> TermData:
        return self.terms[search_term]

    def process_document(self, document_id: str, tokenized_document: list[str]) -> None:
        self.number_of_documents += 1
        document_term_frequencies = Counter(tokenized_document)
        document_length = len(tokenized_document)
        self.document_lengths.append(document_length)

        for term, term_frequency in document_term_frequencies.items():
            term_data = self.get_term_data(term)
            term_data.add_document_info(
                document_id=document_id,
                term_frequency=term_frequency,
                document_length=document_length
            )

    def reset_cached_properties(self: Index):
        """ To be used if the index is ever updated with more articles after instantiation and use. """
        _reset_cached_properties(
            self,
            properties=(
                "average_document_length",
                "corpus_size"
            )
        )
        for term_data in self.terms.values():
            term_data.reset_cached_properties()

