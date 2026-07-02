import secrets
from typing import Annotated, Literal
from pydantic import AnyUrl, BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict

def parse_cors_origins(origins: str) -> list[str] | str:
    """
    Parse a string of CORS origins into a list.

    Args:
        origins (str): A string of CORS origins, separated by commas.

    Returns:
        list: A list of CORS origins.
    """
    if origins.startswith("[") and origins.endswith("]"):
        return [origin.strip() for origin in origins[1:-1].split(",")]
    return [origin.strip() for origin in origins.split(",")]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",     #one level up from the current file
        env_ignore_empty = True,
        extra = "ignore"
    )

    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # JWT token expires after 8 days
    FRONTEND_HOST: str = "http://localhost:5173"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors_origins)
    ] = []
