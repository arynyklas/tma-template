from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from src.application.user.service import TelegramUserSyncData, UserService
from src.domain.user import User
from src.domain.user.vo import (
    Bio,
    FirstName,
    LanguageCode,
    ReferralCount,
    UserId,
    Username,
)


class TestUserService:
    @pytest.fixture
    def mock_user_repo(self):
        return AsyncMock()

    @pytest.fixture
    def user_service(self, mock_user_repo):
        return UserService(mock_user_repo)

    @pytest.fixture
    def base_user(self):
        """Base user with all required fields."""
        now = datetime.now(UTC)
        return User(
            id=UserId(123),
            first_name=FirstName("John"),
            last_name=None,
            username=None,
            bio=None,
            created_at=now,
            updated_at=now,
            last_login_at=now,
        )

    async def test_upsert_new_user(self, user_service, mock_user_repo, base_user):
        """Test creating a new user when user doesn't exist."""
        mock_user_repo.get_user.return_value = None
        mock_user_repo.create_user.return_value = base_user

        data = TelegramUserSyncData(
            id=123,
            username="john_doe",
            first_name="John",
            last_name="Doe",
        )

        result = await user_service.sync_telegram_user(data)

        assert result.id.value == 123
        mock_user_repo.create_user.assert_called_once()
        mock_user_repo.update_user.assert_not_called()

    async def test_upsert_existing_user(self, user_service, mock_user_repo, base_user):
        """Test updating existing user and preserving bio/created_at."""
        existing_user = User(
            id=UserId(123),
            first_name=FirstName("Old"),
            last_name=None,
            username=Username("old_name"),
            bio=Bio("Existing bio"),
            created_at=datetime(2024, 1, 1, tzinfo=UTC),
            updated_at=datetime(2024, 1, 1, tzinfo=UTC),
            last_login_at=datetime(2024, 1, 1, tzinfo=UTC),
        )
        mock_user_repo.get_user.return_value = existing_user

        now = datetime.now(UTC)
        updated_user = User(
            id=UserId(123),
            first_name=FirstName("New"),
            last_name=None,
            username=Username("new_name"),
            bio=existing_user.bio,  # preserved
            created_at=existing_user.created_at,  # preserved
            updated_at=now,
            last_login_at=now,
        )
        mock_user_repo.update_user.return_value = updated_user

        data = TelegramUserSyncData(
            id=123,
            username="new_name",
            first_name="New",
            last_name=None,
        )

        result = await user_service.sync_telegram_user(data)

        assert result.first_name.value == "New"
        mock_user_repo.update_user.assert_called_once()
        mock_user_repo.create_user.assert_not_called()

    async def test_sync_telegram_user_with_no_last_name(
        self, user_service, mock_user_repo, base_user
    ):
        """Test Telegram sync when last_name is None."""
        mock_user_repo.get_user.return_value = None
        mock_user_repo.create_user.return_value = base_user

        data = TelegramUserSyncData(
            id=123,
            username=None,
            first_name="John",
            last_name=None,
        )

        result = await user_service.sync_telegram_user(data)

        assert result.last_name is None
        assert result.username is None

    async def test_sync_telegram_user_with_no_username(
        self, user_service, mock_user_repo, base_user
    ):
        """Test Telegram sync when username is None."""
        mock_user_repo.get_user.return_value = None
        mock_user_repo.create_user.return_value = base_user

        data = TelegramUserSyncData(
            id=123,
            username=None,
            first_name="John",
            last_name="Doe",
        )

        result = await user_service.sync_telegram_user(data)

        assert result.username is None

    async def test_upsert_existing_user_preserves_non_telegram_fields(
        self, user_service, mock_user_repo
    ):
        """Test updating Telegram identity fields without losing persisted state."""
        existing_user = User(
            id=UserId(123),
            first_name=FirstName("Old"),
            last_name=None,
            username=Username("old_name"),
            bio=Bio("Existing bio"),
            created_at=datetime(2024, 1, 1, tzinfo=UTC),
            updated_at=datetime(2024, 1, 2, tzinfo=UTC),
            last_login_at=datetime(2024, 1, 3, tzinfo=UTC),
            referred_by=UserId(999),
            referral_count=ReferralCount(7),
            language_code=LanguageCode("ru"),
        )
        mock_user_repo.get_user.return_value = existing_user
        mock_user_repo.update_user.side_effect = lambda user: user

        result = await user_service.sync_telegram_user(
            TelegramUserSyncData(
                id=123,
                username="new_name",
                first_name="New",
                last_name="Surname",
            )
        )

        assert result.bio == existing_user.bio
        assert result.created_at == existing_user.created_at
        assert result.referred_by == existing_user.referred_by
        assert result.referral_count == existing_user.referral_count
        assert result.language_code == existing_user.language_code
        assert result.first_name.value == "New"
        assert result.last_name is not None
        assert result.last_name.value == "Surname"
        assert result.username is not None
        assert result.username.value == "new_name"
        assert result.updated_at == result.last_login_at
        mock_user_repo.update_user.assert_awaited_once()
