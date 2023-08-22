from __future__ import annotations

import logging
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cached_property
from typing import Iterable, Optional

from index.schema import SearchResult

logger = logging.getLogger(__name__)


def _reset_cached_properties(object_instance, properties: Iterable[str]):
    """ To be used if the index is ever updated with more articles after instantiation and use. """
    for prop in properties:
        if prop in object_instance.__dict__:
            del object_instance.__dict__[prop]


@dataclass
class DocumentTermInfo:
    """ Contains information about the frequency of one specific term in a document, plus the document's length.

    This is a payload used when ranking a matching document when looking up a search term.
    """
    term_frequency: int = 0
    document_length: int = 0


class TermData:
    """
    Contains information about a specific term in the corpus, including a document index for the term.
    """
    document_index: defaultdict[str, DocumentTermInfo]
    corpus_term_frequency: int = 0

    def __init__(
            self,
            document_index: defaultdict[str, DocumentTermInfo] | None = None,
            corpus_term_frequency: int = 0,
    ):
        self.document_index = document_index or defaultdict(DocumentTermInfo)
        self.corpus_term_frequency = corpus_term_frequency

    @cached_property
    def documents_containing_term(self) -> list[str]:
        """ Returns a list of document IDs that contain the term. """
        return list(self.document_index.keys())

    @cached_property
    def number_of_documents_containing_term(self) -> int:
        """ Returns the number of documents that contain the term. """
        return len(self.documents_containing_term)

    def get_document_info(self, document_id: str) -> DocumentTermInfo:
        """ Returns the DocumentTermInfo for the provided document ID. """
        return self.document_index[document_id]

    def add_document_info(self, document_id: str, term_frequency: int, document_length: int) -> None:
        """ Adds a document ID and its DocumentTermInfo (term frequency & length) to the document index. """
        self.document_index[document_id] = DocumentTermInfo(
            term_frequency=term_frequency,
            document_length=document_length
        )

    def reset_cached_properties(self):
        """ To be used if the index is ever updated with more articles after instantiation and use. """
        _reset_cached_properties(
            self,
            properties=(
                "documents_containing_term",
                "number_of_documents_containing_term"
            )
        )


class Index:
    """ Inverted index of processed Wikipedia articles.

    Contains information about the corpus, including a term index for the corpus.
    The term index in turn consists of a document index so that the documents relevant to the term can be easily
    retrieved.
    Other corpus information stored for use in ranking algorithm.
    """
    terms: defaultdict[str, TermData] = defaultdict(TermData)
    number_of_documents: int = 0
    document_lengths: list[int] = []

    def __init__(
            self,
            terms: defaultdict[str, TermData] | None = None,
            number_of_documents: int = 0,
            document_lengths: Optional[list[int]] = None,
    ):
        self.terms = terms or defaultdict(TermData)
        self.number_of_documents = number_of_documents
        self.document_lengths = document_lengths or []

    @cached_property
    def corpus_size(self) -> int:
        return sum(self.document_lengths)

    @cached_property
    def average_document_length(self) -> float:
        if not self.number_of_documents:
            raise ValueError("Cannot calculate average document length without any documents.")
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


INDEX = Index()


def _reset_index():
    global INDEX
    INDEX = Index()


def bm25_rank(
        total_number_of_documents: int,
        number_of_documents_containing_term: int,
        term_frequency_in_document: int,
        document_length: int,
        average_document_length: float,
        b: Optional[float] = None,
        k_1: Optional[float] = None,
):
    """ Rank documents using the Okapi BM25 model https://en.wikipedia.org/wiki/Okapi_BM25.

    If following the original format developed by Stephen E. Robertson & Karen Spärck Jones, coefficient b should be
    kept between 0.5 and 0.8 and coefficient k_1 should be between 1.2 and 2.0
    """
    if b is None:
        b = 0.8  # 0.5 <= b <= 0.8
    if k_1 is None:
        k_1 = 2.0  # 1.2 <= k <= 2.0

    ratio_numerator = total_number_of_documents - number_of_documents_containing_term + 0.5
    ratio_denominator = number_of_documents_containing_term + 0.5
    w_rsj = math.log(ratio_numerator / ratio_denominator)

    b_calc = ((1 - b) + b * (document_length / average_document_length))
    k_1_calc = (k_1 * b_calc + term_frequency_in_document)

    return (term_frequency_in_document / k_1_calc) * w_rsj


def create_or_update_inverted_index(
        articles: list["ArticleSchema"],  # noqa: F821
        index: Optional[Index] = INDEX
):
    """ Creates or updates existing inverted index model, processes articles and populates index with corpus terms. """
    if index:
        index.reset_cached_properties()
    else:
        index = Index()

    for article in articles:
        logger.info(f"Processing article: {article.title}")

        index.process_document(document_id=article.title, tokenized_document=article.tokenized_content)

    logger.info(f"__Number of documents: {index.number_of_documents}")
    logger.info(f"__Corpus size: {index.corpus_size}")
    logger.info(f"__Avg. document length: {index.average_document_length}")
    return index


def get_set_of_documents_containing_terms(index: Index, terms: Iterable[str]) -> set[str]:
    """ Returns a set of document IDs that contain the provided terms. """
    matching_docs = set()
    for term in terms:
        documents_containing_term = index.get_term_data(search_term=term).documents_containing_term
        if not documents_containing_term:
            continue
        matching_docs.update(documents_containing_term)

    return matching_docs


def rank_documents(query_terms: list[str], inverted_index: Index | None = INDEX, **kwargs) -> list[SearchResult]:
    """ Creates a dict of document IDs and ranks for the provided query terms, ordered by rank. """
    results = {}
    query_counter = Counter(query_terms)

    matching_docs = get_set_of_documents_containing_terms(
        index=inverted_index,
        terms=query_counter.keys()
    )

    for document_id in matching_docs:
        document_rank = 0
        for term in query_counter.keys():
            term_data = inverted_index.get_term_data(term)
            document_info = term_data.get_document_info(document_id=document_id)
            if not document_info:
                continue

            rank = bm25_rank(
                total_number_of_documents=inverted_index.number_of_documents,
                number_of_documents_containing_term=term_data.number_of_documents_containing_term,
                term_frequency_in_document=document_info.term_frequency,
                document_length=document_info.document_length,
                average_document_length=inverted_index.average_document_length,
                **kwargs
            )

            # add this score for every occurrence of the term in the doc
            document_rank += (rank * query_counter[term])

        results[document_id] = document_rank

    return [
        SearchResult(title=k, ranking=results[k])
        for k in sorted(results, key=results.get, reverse=True)
    ]
