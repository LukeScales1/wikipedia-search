import logging
import math
from collections import Counter

from requests import Session

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


def create_inverted_index(session: Session, articles: list[Article], text_processor):
    inv_index = {
        "terms": {},
        "n_docs": 0,
        "cl": 0,
        "dl_avg": 0
    }
    doc_lengths = []
    for article in articles:
        logger.debug(article.title)
        doc_term_frequency = Counter()
        doc_text = get_parsed_text(session, article.title)
        doc_text = text_processor(doc_text)

        dl = len(doc_text)
        doc_lengths.append(dl)
        doc_term_frequency.update(doc_text)
        for term in doc_term_frequency.keys():
            try:
                inv_index["terms"][term]
            except KeyError:
                inv_index["terms"][term] = {
                    "docs": {},
                    "c_tf": 0
                }
            term_frequency = doc_term_frequency[term]
            inv_index["terms"][term]["docs"][article.title] = (term_frequency, dl, doc_term_frequency.values())
            inv_index["terms"][term]["c_tf"] += term_frequency
    inv_index["n_docs"] = len(doc_lengths)
    inv_index["cl"] = sum(doc_lengths)
    inv_index["dl_avg"] = sum(doc_lengths) / len(doc_lengths)
    return inv_index


def rank_inverted_docs(query_terms, inverted_index, **kwargs):
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
