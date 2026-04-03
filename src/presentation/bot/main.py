import asyncio
from contextlib import suppress

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError
from dishka.integrations.aiogram import setup_dishka

from src.infrastructure.config import Config
from src.infrastructure.di import (
    AuthProvider,
    DBProvider,
    I18nProvider,
    bootstrap_service,
)
from src.infrastructure.i18n import DEFAULT_LANGUAGE, TranslatorHub
from src.infrastructure.logging import get_logger
from src.presentation.bot.middleware.user_and_locale import UserAndLocaleMiddleware
from src.presentation.bot.routers import setup_routers

logger = get_logger(__name__)


async def notify_admins_on_startup(
    bot: Bot, config: Config, hub: TranslatorHub
) -> None:
    """Send notification to admins when bot starts up."""
    i18n = hub.get_translator_by_locale(DEFAULT_LANGUAGE)
    for admin_id in config.telegram.admin_ids:
        try:
            await bot.send_message(chat_id=admin_id, text=i18n.bot_started())
        except TelegramAPIError as ex:
            logger.warning(
                event="admin_notification_failed",
                message="Failed to notify admin",
                admin_id=admin_id,
                error=str(ex),
            )


async def main() -> None:
    bootstrap = bootstrap_service(
        "tma-template-bot",
        AuthProvider(),
        DBProvider(),
        I18nProvider(),
    )
    config = bootstrap.config

    bot = Bot(
        token=config.telegram.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher()
    main_router = setup_routers()
    dp.include_router(main_router)

    setup_dishka(container=bootstrap.container, router=dp)

    async with bootstrap.container() as request_container:
        hub = await request_container.get(TranslatorHub)

        dp.message.middleware(UserAndLocaleMiddleware())
        dp.callback_query.middleware(UserAndLocaleMiddleware())

        await notify_admins_on_startup(bot, config, hub)

    await dp.start_polling(bot, config=config)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
