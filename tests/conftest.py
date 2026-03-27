import os

import pytest

from src.infrastructure.config import Config, load_config


@pytest.fixture(scope="session")
def test_config() -> Config:
    config = load_config("config-test.yaml")

    if os.environ.get("POSTGRES_TEST_HOST"):
        config.postgres.host = os.environ["POSTGRES_TEST_HOST"]

    elif os.environ.get("POSTGRES_TEST_PORT"):
        config.postgres.port = int(os.environ["POSTGRES_TEST_PORT"])

    return config


pytest_plugins = [
    "tests.utils.model_factories.user",
]
