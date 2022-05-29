import os
from datetime import timedelta
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseSettings, PostgresDsn, validator, EmailStr, AnyHttpUrl


class Settings(BaseSettings):
    # Service Info
    PROJECT_NAME: str = "Testing to Creative"

    # API
    API_V1_STR: str = "/api/v1"

    HOST: str = "127.0.0.1"
    PORT: int = os.getenv("PORT", 8000)

    # Cores
    BACKEND_CORES_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORES_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # PostgresSQL Configuration
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "test_creative")
    POSTGRES_USER: str = os.getenv("POSTGRES_DB", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "0.0.0.0")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")

    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "20"))
    WEB_CONCURRENCY: int = int(os.getenv("WEB_CONCURRENCY", "1"))
    POOL_SIZE: int = max(DB_POOL_SIZE // WEB_CONCURRENCY, 5)

    POSTGRES_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("POSTGRES_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_HOST"),
            port=values.get("POSTGRES_PORT"),
            path=f'/{values.get("POSTGRES_DB") or ""}',
        )

    # Superuser
    # FIRST_SUPERUSER: EmailStr = "root@estesis.tech"
    # FIRST_SUPERUSER_PASSWORD: str = "123123"


settings = Settings()


class CookiesSettings(BaseSettings):
    # Configure application to store and get JWT from cookies
    authjwt_token_location: set = {"cookies"}
    authjwt_algorithm: str = "HS256"

    authjwt_secret_key: str = "secret"  # secrets.token_urlsafe(32)

    auth_access_token_lifetime: int = 60 * 60
    auth_refresh_token_lifetime: int = 15 * 60 * 60 * 24

    access_expires: int = timedelta(minutes=60).total_seconds()
    refresh_expires: int = timedelta(days=15).total_seconds()

    authjwt_access_token_expires: int = timedelta(minutes=60).total_seconds()
    authjwt_refresh_token_expires: int = timedelta(days=15).total_seconds()

    # Only allow JWT cookies to be sent over https
    authjwt_cookie_secure: bool = False
    # Disable CSRF Protection for this example. default is True
    authjwt_cookie_csrf_protect: bool = False

    # Change to "lax" in production to make your website more secure from CSRF Attacks, default is None
    authjwt_cookie_samesite: str = 'lax'  # noqa


cookies_settings = CookiesSettings()
