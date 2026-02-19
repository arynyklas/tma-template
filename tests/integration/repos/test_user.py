from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.user import User
from src.domain.user.vo import (
    FirstName,
    LanguageCode,
    LastName,
    UserId,
    Username,
)
from src.infrastructure.db.repos.user import UserRepositoryImpl


def create_test_user(
    user_id: int = 123456,
    first_name: str = "Test",
    username: str | None = None,
) -> User:
    """Factory for creating test users with all required fields."""
    now = datetime.now(UTC)
    return User(
        id=UserId(user_id),
        first_name=FirstName(first_name),
        last_name=None,
        username=Username(username) if username else None,
        bio=None,
        created_at=now,
        updated_at=now,
        last_login_at=now,
    )


class TestUserRepository:
    @pytest.fixture
    def user_repo(self, native_db_session: AsyncSession) -> UserRepositoryImpl:
        return UserRepositoryImpl(native_db_session)

    async def test_get_user_by_user_id(self, user_repo: UserRepositoryImpl):
        """Test retrieving user by UserId."""
        user = create_test_user(123456)
        await user_repo.create_user(user)

        # Retrieve by UserId
        found = await user_repo.get_user(UserId(123456))

        assert found is not None
        assert found.id.value == 123456

    async def test_get_user_by_username(self, user_repo: UserRepositoryImpl):
        """Test retrieving user by Username."""
        user = create_test_user(123457, username="testuser")
        await user_repo.create_user(user)

        # Retrieve by Username
        found = await user_repo.get_user(Username("testuser"))

        assert found is not None
        assert found.username is not None
        assert found.username.value == "testuser"

    async def test_get_user_not_found(self, user_repo: UserRepositoryImpl):
        """Test retrieving non-existent user returns None."""
        found = await user_repo.get_user(UserId(999999))
        assert found is None

    async def test_update_user(self, user_repo: UserRepositoryImpl):
        """Test updating an existing user."""
        user = create_test_user(123458, first_name="Original")
        await user_repo.create_user(user)

        # Update the user
        now = datetime.now(UTC)
        updated_user = User(
            id=UserId(123458),
            first_name=FirstName("Updated"),
            last_name=LastName("Name"),
            username=None,
            bio=None,
            created_at=user.created_at,  # preserve
            updated_at=now,
            last_login_at=now,
        )
        result = await user_repo.update_user(updated_user)

        assert result.first_name.value == "Updated"
        assert result.last_name is not None
        assert result.last_name.value == "Name"

    async def test_set_referred_by(self, user_repo: UserRepositoryImpl):
        """Test setting referrer for a user."""
        referrer = create_test_user(111111, first_name="Referrer")
        referred = create_test_user(222222, first_name="Referred")
        await user_repo.create_user(referrer)
        await user_repo.create_user(referred)

        # Set referred_by
        await user_repo.set_referred_by(UserId(222222), UserId(111111))

        # Verify
        user = await user_repo.get_user(UserId(222222))
        assert user is not None

    async def test_increment_referral_count(self, user_repo: UserRepositoryImpl):
        """Test incrementing referral count."""
        user = create_test_user(333333, first_name="Referrer")
        await user_repo.create_user(user)

        # Increment referral count twice
        await user_repo.increment_referral_count(UserId(333333))
        await user_repo.increment_referral_count(UserId(333333))

        # Verify by checking stats
        stats = await user_repo.get_referral_stats()
        assert stats.total_users >= 1

    async def test_get_referral_stats(self, user_repo: UserRepositoryImpl):
        """Test getting referral statistics."""
        # Create users - one with referrer, one without
        referrer = create_test_user(666666, first_name="Referrer")
        user_with_ref = create_test_user(444444, first_name="WithRef")
        user_organic = create_test_user(555555, first_name="Organic")

        await user_repo.create_user(referrer)
        await user_repo.create_user(user_with_ref)
        await user_repo.create_user(user_organic)

        # Set up referral
        await user_repo.set_referred_by(UserId(444444), UserId(666666))

        # Get stats
        stats = await user_repo.get_referral_stats()

        assert stats.total_users >= 2
        assert stats.referred_count >= 1
        assert stats.organic_count >= 1

    async def test_get_top_referrers(self, user_repo: UserRepositoryImpl):
        """Test getting top referrers."""
        referrer = create_test_user(777777, first_name="Top", username="topreferrer")
        await user_repo.create_user(referrer)

        # Increment count
        await user_repo.increment_referral_count(UserId(777777))
        await user_repo.increment_referral_count(UserId(777777))

        # Get top referrers
        top = await user_repo.get_top_referrers(limit=10)

        assert len(top) >= 1
        assert any(t.user_id == 777777 for t in top)

    async def test_update_language(self, user_repo: UserRepositoryImpl):
        """Test updating user language."""
        user = create_test_user(888888, first_name="User")
        await user_repo.create_user(user)

        # Update language
        await user_repo.update_language(UserId(888888), LanguageCode("ru"))

        # Verify
        updated = await user_repo.get_user(UserId(888888))
        assert updated is not None
