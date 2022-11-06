import logging
import math
from collections import Counter
from typing import Callable, Iterable, Optional

from requests import Session

from schema.index import Index
from schema.scraper import Article
from services.parser import get_parsed_text

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig()


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
        session: Session,
        articles: list[Article],
        text_processor: Callable[[str], list[str]],
        index: Optional[Index] = None
):
    """ Creates or updates existing inverted index model, processes articles and populates index with corpus terms. """
    if index:
        index.reset_cached_properties()
    else:
        index = Index()

    for article in articles:
        logger.info(f"Processing article: {article.title}")

        doc_text = get_parsed_text(session, article.title)
        doc_text = text_processor(doc_text)

        index.process_document(document_id=article.title, tokenized_document=doc_text)

    logger.info(f"__Number of documents: {index.number_of_documents}")
    logger.info(f"__Corpus size: {index.corpus_size}")
    logger.info(f"__Avg. document length: {index.average_document_length}")
    return index


def get_set_of_documents_containing_terms(index: Index, terms: Iterable[str]) -> set[str]:
    matching_docs = set()
    for term in terms:
        documents_containing_term = index.get_term_data(search_term=term).documents_containing_term
        if not documents_containing_term:
            continue
        matching_docs.update(documents_containing_term)

    return matching_docs


def rank_documents(query_terms: list[str], inverted_index: Index, **kwargs):
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
    return {k: results[k] for k in sorted(results, key=results.get, reverse=True)}
