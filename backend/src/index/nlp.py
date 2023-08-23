import re
from enum import Enum
from typing import Callable

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer


def set_up_nltk():
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('omw-1.4')


class TextProcessorTypes(Enum):
    """ Possible text processors. """
    BASIC = "basic"
    STOPWORD_REMOVAL = "stopword_removal"
    STEMMING = "stemming"
    LEMMATIZATION = "lemmatization"

    @classmethod
    def values(cls):
        """
        Get a list of the values of the enum.
        :return: A list of the values of the enum.
        """
        return [e.value for e in cls]


TextProcessor = Callable[[str], list[str]]


def basic_preprocess(text: str) -> list[str]:
    """ Basic text preprocessing.

    Removes special characters, punctuation, and numbers.
    Replaces hyphens with whitespace to make hyphenated words two individual terms, before replacing double whitespaces
    with single. Lowercases all text. Tokenizes text and returns list of tokens.
    """
    text = text.replace("-", " ").lower()
    text = text.replace("–", " ")
    text = text.replace("—", " ")
    text = text.replace("_", " ")
    # remove odd chars
    text = text.replace('\"', " ")
    text = text.replace('[', " ")
    text = text.replace(']', " ")
    # replace trailing whitespace
    text = text.replace("  ", " ")
    # replace special chars and numbers
    text = re.sub("[-–+'=$%@#/?!.,:;^()0-9]", "", text)
    # tokenize & return
    return text.split()


def stopword_removal(text: str) -> list[str]:
    """ Removes stopwords from text. """
    stop_words = set(stopwords.words('english'))
    return [word for word in basic_preprocess(text) if word not in stop_words]


def stem(text: str) -> list[str]:
    """ Converts words in text to their stem word using the Porter Stemmer."""
    stemmer = PorterStemmer()
    words = stopword_removal(text)
    return [stemmer.stem(word) for word in words]


def lemmatize(text: str) -> list[str]:
    """ Converts words in text to their lemma using the WordNet lemmatizer."""
    lemmatizer = WordNetLemmatizer()
    words = stopword_removal(text)
    return [lemmatizer.lemmatize(w) for w in words]


TEXT_PROCESSORS = {
    TextProcessorTypes.BASIC: basic_preprocess,
    TextProcessorTypes.STOPWORD_REMOVAL: stopword_removal,
    TextProcessorTypes.STEMMING: stem,
    TextProcessorTypes.LEMMATIZATION: lemmatize,
}
