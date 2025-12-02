"""TODO."""

import logging
from typing import Literal, cast, override

import hydra
import hydra.errors
import hydra_zen
from growthbook import UserContext
from growthbook.growthbook_client import GrowthBookClient
from livekit import rtc
from livekit.agents import NOT_GIVEN, NotGiven, llm, stt, tts, vad
from livekit.agents.voice.audio_recognition import TurnDetectionMode
from livekit.agents.voice.room_io.types import (
    NoiseCancellationParams,
    NoiseCancellationSelector,
)
from livekit.plugins import noise_cancellation
from livekit.plugins.turn_detector.english import EnglishModel
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from omegaconf import OmegaConf
from pydantic import TypeAdapter, ValidationError

from gpass.conf import lk_store

logger = logging.getLogger(__name__)
lk_store.add_to_hydra_store()

ADAPTER_TURN_DETECTION = TypeAdapter(
    Literal["stt", "vad", "MultilingualModel", "EnglishModel"]
)
ADAPTER_OVERRIDES = TypeAdapter(list[str])


class LKProviders:
    """TODO."""

    async def noise_cancellation(self) -> NoiseCancellationSelector | None:
        """TODO."""
        return _noise_cancellation_selector

    async def record_enabled(self) -> bool:
        """TODO."""
        return False

    async def turn_detection(self) -> TurnDetectionMode | NotGiven:
        """TODO."""
        return NOT_GIVEN

    async def stt(self, vad: vad.VAD) -> stt.STT:
        """TODO."""
        providers = await self._instantiate(stt.STT)
        return (
            stt.FallbackAdapter(providers, vad=vad)
            if len(providers) > 1
            else providers[0]
        )

    async def _instantiate[T: llm.LLM | stt.STT | tts.TTS](
        self, config_type: type[T]
    ) -> list[T]:
        config_name = config_type.__name__.lower()

        with hydra.initialize(version_base=None):
            try:
                conf = hydra.compose(
                    config_name=config_name,
                    overrides=await self._get_overrides(config_name),
                )
            except hydra.errors.ConfigCompositionException:
                conf = hydra.compose(config_name=config_name)

        _providers_dict = hydra_zen.instantiate(conf)
        providers_dict = cast(
            dict[str, T], OmegaConf.to_container(_providers_dict[config_name])
        )

        return list(providers_dict.values())

    async def _get_overrides(self, _: str) -> list[str] | None:
        return None


class GBLKProviders(LKProviders):
    """TODO."""

    def __init__(self, gb_client: GrowthBookClient) -> None:
        """TODO."""
        self.gb_client = gb_client
        self.user_context = UserContext()
        super().__init__()

    @override
    async def turn_detection(self) -> TurnDetectionMode | NotGiven:
        mode_str = await self._get_feature_value(
            key="livekit:turn_detection", adapter=ADAPTER_TURN_DETECTION, fallback=None
        )
        if mode_str in ["stt", "vad"]:
            return mode_str

        # EOU model hits get_job_context() on init, so they can't be prewarmed
        if mode_str == "EnglishModel":
            return EnglishModel()
        if mode_str == "MultilingualModel":
            return MultilingualModel()

        return await super().turn_detection()

    @override
    async def noise_cancellation(self) -> NoiseCancellationSelector | None:
        if await self.gb_client.is_on("livekit:noise_cancellation", self.user_context):
            return _noise_cancellation_selector
        return await super().noise_cancellation()

    @override
    async def record_enabled(self) -> bool:
        return await self.gb_client.is_on("livekit:record", self.user_context)

    @override
    async def _get_overrides(self, config_name: str) -> list[str] | None:
        return await self._get_feature_value(
            f"livekit:{config_name}", adapter=ADAPTER_OVERRIDES, fallback=None
        )

    async def _get_feature_value[T](
        self, key: str, adapter: TypeAdapter[T], fallback: T
    ) -> T:
        # TODO typing with Pydantic
        raw_value = await self.gb_client.get_feature_value(
            key=key, fallback=fallback, user_context=self.user_context
        )
        if raw_value == fallback:
            return fallback

        try:
            return adapter.validate_python(raw_value)
        except ValidationError:
            return fallback


def _noise_cancellation_selector(params: NoiseCancellationParams):
    return (
        noise_cancellation.BVCTelephony()
        if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
        else noise_cancellation.BVC()
    )
