import pytest

from src.infrastructure.validators import HttpUrl, Url


class TestUrl:
    @pytest.fixture
    def validator(self) -> Url:
        return Url()

    @pytest.mark.parametrize(
        "url",
        [
            "https://example.com",
            "http://example.com",
            "http://example.com:8080",
            "https://example.com/path",
            "https://example.com/path?query=1",
            "https://user:pass@example.com",
            "ftp://files.example.com/data",
            "postgresql+asyncpg://user:pass@localhost:5432/db",
            "redis://localhost:6379",
        ],
    )
    def test_valid_urls(self, validator: Url, url: str) -> None:
        validate = validator.get_validator_func()
        assert validate(url) is True

    @pytest.mark.parametrize(
        "url",
        [
            "",
            "not-a-url",
            "://missing-scheme",
            "http://",
            "just-a-host.com",
            "/relative/path",
        ],
    )
    def test_invalid_urls(self, validator: Url, url: str) -> None:
        validate = validator.get_validator_func()
        assert validate(url) is False

    def test_error_message_default(self) -> None:
        validator = Url()
        assert (
            validator.get_error_message()
            == "Value must be a valid URL with scheme and host"
        )

    def test_error_message_custom(self) -> None:
        validator = Url(error_message="Bad URL")
        assert validator.get_error_message() == "Bad URL"


class TestHttpUrl:
    @pytest.fixture
    def validator(self) -> HttpUrl:
        return HttpUrl()

    @pytest.mark.parametrize(
        "url",
        [
            "https://example.com",
            "http://example.com",
            "https://example.com:8080",
            "https://example.com/path",
            "https://example.com/path?query=1&other=2",
            "https://user:pass@example.com",
            "http://localhost:4318",
            "https://public@example.ingest.sentry.io/123",
        ],
    )
    def test_valid_http_urls(self, validator: HttpUrl, url: str) -> None:
        validate = validator.get_validator_func()
        assert validate(url) is True

    @pytest.mark.parametrize(
        "url",
        [
            "",
            "not-a-url",
            "ftp://files.example.com",
            "postgresql://user:pass@localhost/db",
            "redis://localhost:6379",
            "://missing-scheme",
            "http://",
            "just-a-host.com",
            "/relative/path",
        ],
    )
    def test_invalid_http_urls(self, validator: HttpUrl, url: str) -> None:
        validate = validator.get_validator_func()
        assert validate(url) is False

    def test_error_message_default(self) -> None:
        validator = HttpUrl()
        assert validator.get_error_message() == "Value must be a valid HTTP(S) URL"

    def test_error_message_custom(self) -> None:
        validator = HttpUrl(error_message="Must be HTTP")
        assert validator.get_error_message() == "Must be HTTP"


class TestValidatorProtocolCompliance:
    """Verify validators satisfy the dature ValidatorProtocol contract."""

    @pytest.mark.parametrize("cls", [Url, HttpUrl])
    def test_has_get_validator_func(self, cls: type) -> None:
        instance = cls()
        func = instance.get_validator_func()
        assert callable(func)

    @pytest.mark.parametrize("cls", [Url, HttpUrl])
    def test_has_get_error_message(self, cls: type) -> None:
        instance = cls()
        msg = instance.get_error_message()
        assert isinstance(msg, str)
        assert len(msg) > 0

    @pytest.mark.parametrize("cls", [Url, HttpUrl])
    def test_is_frozen_dataclass(self, cls: type) -> None:
        instance = cls()
        with pytest.raises(AttributeError):
            instance.error_message = "mutated"  # type: ignore[misc]
