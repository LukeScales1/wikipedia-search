from collections import Counter

from requests import Session

from schema.scraper import Article
from services.parser import get_parsed_text


def create_inverted_index(session: Session, articles: list[Article], text_processor):
    inv_index = {
        "terms": {},
        "n_docs": 0,
        "cl": 0,
        "dl_avg": 0
    }
    doc_lengths = []
    for article in articles:
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
