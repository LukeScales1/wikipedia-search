import re

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer


def set_up_nltk():
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('omw-1.4')


def basic_preprocess(text):
    # BASIC PREPROCESS: remove special characters, punctuation, numbers
    # replace hyphens w/ whitespace - make hyphenated words two individual terms; lowercase
    text = text.replace("-", " ").lower()
    text = text.replace("–", " ")
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


def stopword_removal(text):
    stop_words = set(stopwords.words('english'))
    return [word for word in basic_preprocess(text) if word not in stop_words]


def stem(text):
    stemmer = PorterStemmer()
    words = stopword_removal(text)
    return [stemmer.stem(word) for word in words]


def lemmatize(text):
    lemmatizer = WordNetLemmatizer()
    words = stopword_removal(text)
    return [lemmatizer.lemmatize(w) for w in words]
