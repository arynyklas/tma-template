from src.application.common.interactor import Interactor
from src.application.common.transaction import TransactionManager
from src.application.user.dtos import (
    SyncTelegramUserInputDTO,
    SyncTelegramUserOutputDTO,
    entity_to_dto,
)
from src.application.user.service import TelegramUserSyncData, UserService


class SyncTelegramUserInteractor(
    Interactor[SyncTelegramUserInputDTO, SyncTelegramUserOutputDTO]
):
    def __init__(
        self,
        user_service: UserService,
        transaction_manager: TransactionManager,
    ) -> None:
        self.user_service = user_service
        self.transaction_manager = transaction_manager

    async def __call__(
        self, data: SyncTelegramUserInputDTO
    ) -> SyncTelegramUserOutputDTO:
        user = await self.user_service.sync_telegram_user(
            TelegramUserSyncData(
                id=data.id,
                username=data.username,
                first_name=data.first_name,
                last_name=data.last_name,
            )
        )

        await self.transaction_manager.commit()

        return entity_to_dto(user)
