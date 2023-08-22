"""
This file contains all the settings for the application.
"""
import logging

from index.nlp import lemmatize, set_up_nltk

logging.basicConfig()

set_up_nltk()

text_processor = lemmatize

NUMBER_OF_ARTICLES = 10

DB_CONNECTION = "postgresql+psycopg2://postgres:password@db:5432/wiki-search"
