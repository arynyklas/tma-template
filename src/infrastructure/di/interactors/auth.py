from dishka import Provider, Scope, provide

from src.application.auth.tg import AuthTgInteractor
from src.application.common.transaction import TransactionManager
from src.application.interfaces.auth import AuthService
from src.domain.user import UserRepository


class AuthInteractorProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def provide_auth_tg_interactor(
        self,
        user_repository: UserRepository,
        transaction_manager: TransactionManager,
        auth_service: AuthService,
    ) -> AuthTgInteractor:
        return AuthTgInteractor(
            user_repository,
            transaction_manager,
            auth_service,
        )
