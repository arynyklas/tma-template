from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from src.application.user.service import UpsertUserData, UserService
from src.domain.user import User
from src.domain.user.vo import Bio, FirstName, UserId, Username


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

        data = UpsertUserData(
            id=123,
            username="john_doe",
            first_name="John",
            last_name="Doe",
        )

        result = await user_service.upsert_user(data)

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

        data = UpsertUserData(
            id=123,
            username="new_name",
            first_name="New",
            last_name=None,
        )

        result = await user_service.upsert_user(data)

        assert result.first_name.value == "New"
        mock_user_repo.update_user.assert_called_once()
        mock_user_repo.create_user.assert_not_called()

    async def test_upsert_user_with_no_last_name(
        self, user_service, mock_user_repo, base_user
    ):
        """Test upsert when last_name is None."""
        mock_user_repo.get_user.return_value = None
        mock_user_repo.create_user.return_value = base_user

        data = UpsertUserData(
            id=123,
            username=None,
            first_name="John",
            last_name=None,
        )

        result = await user_service.upsert_user(data)

        assert result.last_name is None
        assert result.username is None

    async def test_upsert_user_with_no_username(
        self, user_service, mock_user_repo, base_user
    ):
        """Test upsert when username is None."""
        mock_user_repo.get_user.return_value = None
        mock_user_repo.create_user.return_value = base_user

        data = UpsertUserData(
            id=123,
            username=None,
            first_name="John",
            last_name="Doe",
        )

        result = await user_service.upsert_user(data)

        assert result.username is None
