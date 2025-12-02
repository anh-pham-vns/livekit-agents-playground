"""TODO."""

import logging
from enum import StrEnum
from typing import Protocol

from hydra_zen import ZenStore, make_config
from hydra_zen.typing import Builds

from . import _llm, _stt, _tts

logger = logging.getLogger(__name__)


class _ProviderModule[P, T](Protocol):
    Provider: type[P]
    REGISTRY: dict[P, Builds[type[T]]]
    __name__: str


# Change the LiveKit providers here
DEFAULTS: dict[_ProviderModule, list[StrEnum]] = {
    _llm: [_llm.Provider.Sonnet_4_0, _llm.Provider.Sonnet_4_5],
    _stt: [_stt.Provider.Chirp_3, _stt.Provider.Transcribe],
    _tts: [_tts.Provider.Chirp_3],
}

lk_store = ZenStore()

for module, default_list in DEFAULTS.items():
    selected_set = set(default_list)
    registered_set = set(module.REGISTRY.keys())
    # _llm.py -> module=_llm -> group="llm" :D
    group = module.__name__.split(".")[-1].lstrip("_")

    if not selected_set.issubset(registered_set):
        unregistered_providers = selected_set - registered_set
        logger.error(
            "Missing %s credentials: %s", group, ",".join(unregistered_providers)
        )

        # Remove unregistered providers, keep order with list comprehension
        providers = [p for p in default_list if p in module.REGISTRY]

        # If the specified list is empty -> fallback to use all registered
        DEFAULTS[module] = providers if providers else list(module.REGISTRY.keys())

    # Save `provider_name` into group: llm/provider_name
    m_store = lk_store(group=group)
    for provider, conf in module.REGISTRY.items():
        m_store({provider: conf}, name=provider)

    # Store the selection: config_name = "llm"
    lk_store(
        make_config(hydra_defaults=[{group: DEFAULTS[module]}, "_self_"]),
        name=group,
    )
