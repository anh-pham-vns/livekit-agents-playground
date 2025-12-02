"""TODO."""

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class _GrowthBook(BaseSettings):
    client_key: SecretStr


class Settings(BaseSettings):
    """TODO."""

    model_config = SettingsConfigDict(env_nested_delimiter="_", env_nested_max_split=1)

    growthbook: _GrowthBook
    # record_dir: UPathField


settings = Settings.model_validate({})
