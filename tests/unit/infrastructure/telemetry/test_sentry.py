import asyncio
from unittest.mock import Mock

from src.infrastructure.config import TelemetryConfig, load_config
from src.infrastructure.telemetry.sentry import init_sentry
from src.presentation.api.app import create_app
from src.presentation.bot.main import main


def test_init_sentry_is_defined() -> None:
    assert callable(init_sentry)


def test_init_sentry_noops_without_dsn(monkeypatch) -> None:
    init_mock = Mock()
    monkeypatch.setattr(
        "src.infrastructure.telemetry.sentry.sentry_sdk.init", init_mock
    )

    config = TelemetryConfig.model_validate(
        {
            "alloy_base": "https://alloy.example.com",
            "export_metrics": True,
            "export_traces": True,
            "sentry_dsn": None,
        }
    )
    init_sentry(config, service_name="tma-template-api")

    init_mock.assert_not_called()


def test_init_sentry_configures_sdk_with_full_tracing(monkeypatch) -> None:
    init_mock = Mock()
    monkeypatch.setattr(
        "src.infrastructure.telemetry.sentry.sentry_sdk.init", init_mock
    )

    config = TelemetryConfig.model_validate(
        {
            "alloy_base": "https://alloy.example.com",
            "export_metrics": True,
            "export_traces": True,
            "sentry_dsn": "https://public@example.ingest.sentry.io/123",
            "sentry_environment": "production",
            "sentry_release": "backend@prod-a1b2c3d",
            "sentry_traces_sample_rate": 1.0,
        }
    )
    init_sentry(config, service_name="tma-template-api")

    init_mock.assert_called_once()
    kwargs = init_mock.call_args.kwargs
    assert kwargs["dsn"] == "https://public@example.ingest.sentry.io/123"
    assert kwargs["environment"] == "production"
    assert kwargs["release"] == "backend@prod-a1b2c3d"
    assert kwargs["traces_sample_rate"] == 1.0


def test_init_sentry_enables_local_variable_capture(monkeypatch) -> None:
    init_mock = Mock()
    monkeypatch.setattr(
        "src.infrastructure.telemetry.sentry.sentry_sdk.init", init_mock
    )

    config = TelemetryConfig.model_validate(
        {
            "alloy_base": "https://alloy.example.com",
            "export_metrics": True,
            "export_traces": True,
            "sentry_dsn": "https://public@example.ingest.sentry.io/123",
        }
    )
    init_sentry(config, service_name="tma-template-api")

    kwargs = init_mock.call_args.kwargs
    assert kwargs["include_local_variables"] is True


def test_create_app_initializes_sentry(monkeypatch) -> None:
    init_mock = Mock()
    config = load_config("config-test.yaml")

    monkeypatch.setattr("src.presentation.api.app.init_sentry", init_mock)
    monkeypatch.setattr("src.presentation.api.app.load_config", lambda: config)

    create_app()

    init_mock.assert_called_once_with(config.telemetry, service_name="tma-template-api")


def test_bot_main_initializes_sentry(monkeypatch) -> None:
    init_mock = Mock()
    config = load_config("config-test.yaml")

    monkeypatch.setattr("src.presentation.bot.main.init_sentry", init_mock)
    monkeypatch.setattr("src.presentation.bot.main.load_config", lambda: config)

    async def fake_notify_admins_on_startup(*_args, **_kwargs) -> None:
        return None

    async def fake_start_polling(*_args, **_kwargs) -> None:
        return None

    monkeypatch.setattr(
        "src.presentation.bot.main.notify_admins_on_startup",
        fake_notify_admins_on_startup,
    )
    monkeypatch.setattr("aiogram.Dispatcher.start_polling", fake_start_polling)

    asyncio.run(main())

    init_mock.assert_called_once_with(config.telemetry, service_name="tma-template-bot")
