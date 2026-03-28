from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from aiogram.types import CallbackQuery, Message
from aiogram.types import User as AiogramUser
from dishka.integrations.aiogram import CONTAINER_NAME
import pytest

from src.application.user.dtos import SyncTelegramUserOutputDTO
from src.infrastructure.i18n import TranslatorHub, create_translator_hub
from src.presentation.bot.middleware.user_and_locale import UserAndLocaleMiddleware


class TestUserAndLocaleMiddleware:
    @pytest.fixture
    def hub(self) -> TranslatorHub:
        locales_dir = Path(__file__).parent.parent.parent.parent.parent / "locales"
        return create_translator_hub(locales_dir)

    @pytest.fixture
    def middleware(self) -> UserAndLocaleMiddleware:
        return UserAndLocaleMiddleware()

    @pytest.fixture
    def from_user(self) -> MagicMock:
        user = MagicMock(spec=AiogramUser)
        user.id = 123456
        user.username = "telegram_user"
        user.first_name = "Telegram"
        user.last_name = "User"
        user.language_code = "ru"
        return user

    @pytest.fixture
    def event(self, from_user: MagicMock) -> MagicMock:
        event = MagicMock(spec=Message)
        event.from_user = from_user
        return event

    @pytest.fixture
    def container(self, hub: TranslatorHub) -> MagicMock:
        container = MagicMock()
        container.get = AsyncMock(side_effect=[AsyncMock(), hub])
        return container

    async def test_prefers_persisted_language_over_telegram_language(
        self,
        middleware: UserAndLocaleMiddleware,
        event: MagicMock,
        container: MagicMock,
        hub: TranslatorHub,
    ) -> None:
        handler = AsyncMock(return_value="handled")
        sync_user = AsyncMock(
            return_value=SyncTelegramUserOutputDTO(
                id=123456,
                username="telegram_user",
                first_name="Telegram",
                last_name="User",
                language_code="en",
                is_new=False,
            )
        )
        container.get = AsyncMock(side_effect=[sync_user, hub])
        data = {CONTAINER_NAME: container}

        result = await middleware(handler, event, data)

        assert result == "handled"
        assert data["user"].language_code == "en"
        assert data["i18n"].get("welcome", name="Test") == (
            hub.get_translator_by_locale("en").get("welcome", name="Test")
        )
        handler.assert_awaited_once()

    async def test_falls_back_to_telegram_language_when_persisted_missing(
        self,
        middleware: UserAndLocaleMiddleware,
        event: MagicMock,
        container: MagicMock,
        hub: TranslatorHub,
    ) -> None:
        handler = AsyncMock(return_value="handled")
        sync_user = AsyncMock(
            return_value=SyncTelegramUserOutputDTO(
                id=123456,
                username="telegram_user",
                first_name="Telegram",
                last_name="User",
                language_code=None,
                is_new=False,
            )
        )
        container.get = AsyncMock(side_effect=[sync_user, hub])
        data = {CONTAINER_NAME: container}

        result = await middleware(handler, event, data)

        assert result == "handled"
        assert data["user"].language_code is None
        assert data["i18n"].get("welcome", name="Тест") == (
            hub.get_translator_by_locale("ru").get("welcome", name="Тест")
        )
        handler.assert_awaited_once()

    async def test_skips_sync_when_event_has_no_user(
        self, middleware: UserAndLocaleMiddleware, container: MagicMock
    ) -> None:
        handler = AsyncMock(return_value="handled")
        event = MagicMock(spec=CallbackQuery)
        event.from_user = None
        data = {CONTAINER_NAME: container}

        result = await middleware(handler, event, data)

        assert result == "handled"
        container.get.assert_not_called()
        handler.assert_awaited_once_with(event, data)
