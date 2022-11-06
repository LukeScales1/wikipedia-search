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


def bm25_rank(N, n, tf, dl, dl_avg, b=None, k_1=None):
    if b is None:
        b = 0.8  # 0.5 <= b <= 0.8
    if k_1 is None:
        k_1 = 2  # 1.2 <= k <= 2
    w_rsj = math.log(((N - n + 0.5) / (n + 0.5)))
    return (tf / (k_1 * ((1 - b) + b*(dl/dl_avg)) + tf)) * w_rsj


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
                N=inverted_index["n_docs"], n=len(inverted_index["terms"][term]["docs"].keys()), tf=doc_entry[0],
                dl=doc_entry[1], dl_avg=inverted_index["dl_avg"], **kwargs)

            for i in range(query_counter[term]):
                doc_rank.append(rank)

        results[doc] = sum(doc_rank)
    return {k: results[k] for k in sorted(results, key=results.get, reverse=True)}
