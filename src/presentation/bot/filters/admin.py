from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message

from src.infrastructure.config import Config


class AdminFilter(Filter):
    async def __call__(self, obj: Message | CallbackQuery, config: Config) -> bool:
        """
        Args:
            obj (Update): Aiogram injects it to the the filter.
            config (Config): Aiogram injects it to the the filter.
        """
        assert obj.from_user is not None, (
            "Expected from_user to be present in the update"
        )

        return obj.from_user.id in config.telegram.admin_ids
