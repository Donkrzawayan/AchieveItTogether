from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    DISCORD_TOKEN: SecretStr
    ALLOWED_ROLE_ID: int

    @property
    def database_url(self) -> str:
        return "sqlite+aiosqlite:///achievebot.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings() # pyright: ignore[reportCallIssue]
