from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from dishka import AsyncContainer, Provider, make_async_container

from src.infrastructure.config import Config, load_config
from src.infrastructure.di.interactors import interactor_providers
from src.infrastructure.logging import configure_logging
from src.infrastructure.telemetry import init_sentry

ContextBuilder = Callable[[Config], Mapping[type[Any], object]]


@dataclass(frozen=True, slots=True)
class ServiceBootstrap:
    config: Config
    container: AsyncContainer


def bootstrap_service(
    service_name: str,
    *providers: Provider,
    context_builder: ContextBuilder | None = None,
) -> ServiceBootstrap:
    """Perform the shared service bootstrap sequence.

    The caller stays responsible for transport-specific wiring; this helper only
    handles the shared startup path and returns the assembled values explicitly.
    """

    configure_logging(service_name)
    config = load_config()
    init_sentry(config.telemetry, service_name=service_name)

    interactor_provider_instances = [provider() for provider in interactor_providers]
    context: dict[type[Any], object] = {Config: config}
    if context_builder is not None:
        context.update(context_builder(config))

    container = make_async_container(
        *providers,
        *interactor_provider_instances,
        context=context,
    )
    return ServiceBootstrap(config=config, container=container)
