from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.application.common.transaction import TransactionManager
from src.domain.user import UserRepository
from src.infrastructure.config import PostgresConfig


class DBProvider(Provider):
    scope = Scope.APP

    @provide(scope=Scope.REQUEST)
    async def get_transaction_manager(
        self,
    ) -> TransactionManager:
        return TransactionManager

    @provide(scope=Scope.REQUEST)
    async def get_user_repository(
        self,
    ) -> UserRepository:
        return UserRepository
