from dishka import Provider

from .admin import AdminInteractorProvider
from .auth import AuthInteractorProvider
from .referral import ReferralInteractorProvider
from .user import UserInteractorProvider

interactor_providers: list[type[Provider]] = [
    AdminInteractorProvider,
    AuthInteractorProvider,
    ReferralInteractorProvider,
    UserInteractorProvider,
]

__all__ = [
    "AdminInteractorProvider",
    "AuthInteractorProvider",
    "ReferralInteractorProvider",
    "UserInteractorProvider",
    "interactor_providers",
]
