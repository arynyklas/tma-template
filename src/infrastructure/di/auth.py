from dishka import Provider, Scope, from_context, provide

from src.application.interfaces.auth import AuthService
from src.infrastructure.auth import AuthServiceImpl
from src.infrastructure.config import Config


class AuthProvider(Provider):
    scope = Scope.APP
    config = from_context(Config)

    @provide
    def get_auth_service(self, config: Config) -> AuthService:
        return AuthServiceImpl(config)
