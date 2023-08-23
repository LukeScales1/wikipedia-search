"""
This file contains all the settings for the application.
"""
import logging
from typing import Any, Tuple, Type

from pydantic import PostgresDsn
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, EnvSettingsSource, PydanticBaseSettingsSource, SettingsConfigDict

from index.nlp import TEXT_PROCESSORS, TextProcessor, TextProcessorTypes, lemmatize, set_up_nltk

logging.basicConfig()

set_up_nltk()


class TextProcessorSource(EnvSettingsSource):
    def prepare_field_value(
        self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool
    ) -> Any:
        if field_name == 'text_processor' and value:
            if value not in (valid_entries := TextProcessorTypes.values()):
                raise ValueError(
                    f"Invalid text processor '{value}', must be one of {valid_entries}"
                )
            return TEXT_PROCESSORS[TextProcessorTypes(value)]
        return value


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    postgres_user: str = "test"
    postgres_password: str = "test"
    postgres_db: str = "test"
    postgres_host: str = "test"
    postgres_port: int = 0000
    default_number_of_articles: int = 10
    text_processor: TextProcessor = lemmatize

    @property
    def postgres_dsn(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme='postgresql+psycopg2',
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            path=self.postgres_db,
        )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (TextProcessorSource(settings_cls),)
