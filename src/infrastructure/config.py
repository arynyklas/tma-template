import os
from pathlib import Path

from pydantic import BaseModel, Field, HttpUrl
import yaml


class PostgresConfig(BaseModel):
    host: str
    port: int = Field(gt=0, lt=65536)
    user: str
    password: str
    db: str
    echo: bool = False
    pool_size: int = 30
    pool_timeout: int = 30
    pool_recycle: int = 3600
    max_overflow: int = 20
    pool_pre_ping: bool = True
    echo_pool: bool = False

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class AuthConfig(BaseModel):
    secret_key: str = Field(min_length=32)
    algorithm: str
    access_token_expire_minutes: int


class TelemetryConfig(BaseModel):
    alloy_base: HttpUrl = Field(description="Base URL for Alloy OTLP HTTP receiver")
    export_metrics: bool = True
    export_traces: bool = True
    sentry_dsn: HttpUrl | None = Field(default=None, description="Sentry DSN")
    sentry_environment: str | None = None
    sentry_release: str | None = None
    sentry_traces_sample_rate: float = Field(default=1.0, ge=0.0, le=1.0)
    sentry_ca_certs: str | None = Field(
        default=None,
        description="Path to custom CA certificate for Sentry SSL verification",
    )


class TelegramConfig(BaseModel):
    bot_token: str
    admin_ids: list[int]
    bot_username: str
    tg_init_data: str | None = Field(
        default=None, description="Telegram init data for testing purposes"
    )


class Config(BaseModel):
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

    with file_path.open("r") as file:
        return Config.model_validate(yaml.safe_load(file))
