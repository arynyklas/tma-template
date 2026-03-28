"""Middleware that synchronizes Telegram users and injects i18n context."""

from collections.abc import Awaitable, Callable
from typing import Any, cast

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.types import User as AiogramUser
from dishka import AsyncContainer
from dishka.integrations.aiogram import CONTAINER_NAME

from src.application.user.create import SyncTelegramUserInteractor
from src.application.user.dtos import (
    SyncTelegramUserInputDTO,
    SyncTelegramUserOutputDTO,
)
from src.infrastructure.i18n import TranslatorHub
from src.presentation.bot.utils.i18n import extract_language_code


class UserAndLocaleMiddleware(BaseMiddleware):
    """Synchronize Telegram user state and inject `user` plus `i18n`.

    The middleware preserves persisted locale preference when available and
    falls back to the Telegram-provided language for first-contact users.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:  # noqa: ANN401
        from_user: AiogramUser | None = getattr(event, "from_user", None)
        if from_user is None:
            return await handler(event, data)

        container = cast(AsyncContainer, data[CONTAINER_NAME])
        sync_user_interactor = await container.get(SyncTelegramUserInteractor)
        hub = await container.get(TranslatorHub)

        user_dto: SyncTelegramUserOutputDTO = await sync_user_interactor(
            data=SyncTelegramUserInputDTO(
                id=from_user.id,
                username=from_user.username,
                first_name=from_user.first_name,
                last_name=from_user.last_name,
            )
        )

        # Get locale: prefer saved language, fallback to Telegram language
        if user_dto.language_code:
            locale = user_dto.language_code
        else:
            locale = extract_language_code(from_user.language_code)

        data["user"] = user_dto
        data["i18n"] = hub.get_translator_by_locale(locale)

        return await handler(event, data)
