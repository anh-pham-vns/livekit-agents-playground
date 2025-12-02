"""TODO."""

import growthbook
from dependency_injector import containers, providers
from growthbook.growthbook_client import GrowthBookClient

from gpass.conf.settings import settings

from ..services.livekit import LKProviders


class Container(containers.DeclarativeContainer):
    """https://python-dependency-injector.ets-labs.org/containers/index.html."""

    growthbook = providers.Resource(
        GrowthBookClient,
        options=growthbook.Options(
            client_key=settings.growthbook.client_key.get_secret_value()
        ),
    )

    lk_provider = providers.Singleton(LKProviders, growthbook=growthbook)
