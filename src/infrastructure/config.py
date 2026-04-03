from dataclasses import dataclass
import os
from pathlib import Path
from typing import Annotated

from dature import Source, load
from dature.fields.secret_str import SecretStr
from dature.validators.number import Ge, Gt, Le, Lt
from dature.validators.string import MinLength

from src.infrastructure.validators import HttpUrl


@dataclass
class PostgresConfig:
    host: str
    port: Annotated[int, Gt(value=0), Lt(value=65536)]
    user: str
    password: SecretStr
    db: str
    echo: bool = False
    pool_size: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    max_overflow: int = 20
    pool_pre_ping: bool = True
    echo_pool: bool = False

    def get_url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.db}"


@dataclass
class AuthConfig:
    secret_key: Annotated[SecretStr, MinLength(value=32)]
    algorithm: Annotated[str, MinLength(value=1)]
    access_token_expire_minutes: Annotated[int, Gt(value=0)]


@dataclass
class TelemetryConfig:
    alloy_base: Annotated[SecretStr, HttpUrl()]
    export_metrics: bool = True
    export_traces: bool = True
    sentry_dsn: Annotated[SecretStr, HttpUrl()] | None = None
    sentry_traces_sample_rate: Annotated[float, Ge(value=0.0), Le(value=1.0)] = 1.0
    sentry_ca_certs: str | None = None


@dataclass
class TelegramConfig:
    bot_token: SecretStr
    admin_ids: list[int]
    bot_username: str
    tg_init_data: SecretStr | None = None


@dataclass
class Config:
    postgres: PostgresConfig
    auth: AuthConfig
    telemetry: TelemetryConfig
    telegram: TelegramConfig


def load_config(file_name: str | None = None) -> Config:
    if file_name is None:
        file_name = os.environ.get("CONFIG_PATH", "config.yaml")

    file_path = Path(file_name)

    if not file_path.is_file():
        raise FileNotFoundError(f"Config file '{file_name}' not found")

    return load(Source(file_=file_path), Config)
