from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol, overload

from src.domain.user.entity import User
from src.domain.user.vo import LanguageCode, UserId, Username


@dataclass
class ReferralStats:
    total_users: int
    referred_count: int
    organic_count: int


@dataclass
class TopReferrer:
    user_id: int
    username: str | None
    first_name: str
    referral_count: int


class UserRepository(Protocol):
    @abstractmethod
    @overload
    async def get_user(self, identifier: UserId) -> User | None: ...

    @abstractmethod
    @overload
    async def get_user(self, identifier: Username) -> User | None: ...

    @abstractmethod
    async def get_user(self, identifier: UserId | Username) -> User | None: ...

    @abstractmethod
    async def create_user(self, user: User) -> User: ...

    @abstractmethod
    async def update_user(self, user: User) -> User: ...

    @abstractmethod
    async def delete_user(self, user_id: UserId) -> None: ...

    @abstractmethod
    async def set_referred_by(self, user_id: UserId, referrer_id: UserId) -> None: ...

    @abstractmethod
    async def increment_referral_count(self, user_id: UserId) -> None: ...

    @abstractmethod
    async def get_referral_stats(self) -> ReferralStats: ...

    @abstractmethod
    async def get_top_referrers(self, limit: int = 10) -> list[TopReferrer]: ...

    @abstractmethod
    async def update_language(
        self, user_id: UserId, language_code: LanguageCode
    ) -> None: ...
