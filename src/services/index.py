import logging
import math
from collections import Counter
from typing import Callable, Optional

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


def rank_inverted_docs(query_terms: list[str], inverted_index: Index, **kwargs):
    results = {}
    query_counter = Counter()
    query_counter.update(query_terms)
    matching_docs = set()
    for query in query_counter.keys():
        try:
            doc_ids = inverted_index["terms"][query]["docs"].keys()
            matching_docs.update(doc_ids)
        except KeyError:
            # query term not present in doc corpus
            continue
    for doc in matching_docs:
        doc_rank = []
        for term in query_counter.keys():
            try:
                doc_entry = inverted_index["terms"][term]["docs"][doc]
            except KeyError:
                continue

            rank = bm25_rank(
                total_number_of_documents=inverted_index["n_docs"],
                number_of_documents_containing_term=len(inverted_index["terms"][term]["docs"].keys()),
                term_frequency_in_document=doc_entry[0],
                document_length=doc_entry[1],
                average_document_length=inverted_index["dl_avg"],
                **kwargs
                )

            for i in range(query_counter[term]):
                doc_rank.append(rank)

        results[doc] = sum(doc_rank)
    return {k: results[k] for k in sorted(results, key=results.get, reverse=True)}
