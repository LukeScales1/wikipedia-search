"""
This file contains all the settings for the application.
"""
import logging

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

from index.nlp import lemmatize, set_up_nltk

logging.basicConfig()

set_up_nltk()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    pg_dsn: PostgresDsn = 'postgresql+psycopg2://postgres:password@db:5432/wiki-search'
    default_number_of_articles: int = 10


text_processor = lemmatize
