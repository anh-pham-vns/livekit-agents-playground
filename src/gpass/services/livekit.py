"""TODO."""

import logging
from typing import Any

from growthbook import UserContext
from growthbook.growthbook_client import GrowthBookClient
from livekit import rtc
from livekit.agents import NOT_GIVEN, NotGiven
from livekit.agents.voice.audio_recognition import TurnDetectionMode
from livekit.agents.voice.room_io.types import (
    NoiseCancellationParams,
    NoiseCancellationSelector,
)
from livekit.plugins import noise_cancellation
from livekit.plugins.turn_detector.english import EnglishModel
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from gpass.plugins import google

logger = logging.getLogger(__name__)


class LKProviders:
    """TODO."""

    def __init__(self, growthbook: GrowthBookClient) -> None:
        """TODO."""
        self.growthbook = growthbook
        self.user_context = UserContext()

    async def noise_cancellation(self) -> NoiseCancellationSelector | None:
        """TODO."""
        return (
            _get_noise_cancellation
            if await self.growthbook.is_on(
                "livekit:noise_cancellation", self.user_context
            )
            else None
        )

    async def record_enabled(self) -> bool:
        """TODO."""
        return await self.growthbook.is_on("livekit:record", self.user_context)

    async def stt(self):
        """TODO."""
        _denoise_profile = await self._get_feature_value(
            "livekit:stt.chirp3.denoise_profile", fallback=None
        )
        try:
            denoiser_config = google.DenoiseProfile[_denoise_profile].value
        except KeyError:
            denoiser_config = None

        use_streaming = await self.growthbook.is_on(
            "livekit:stt.chirp3.use_streaming", self.user_context
        )

        return google.STT(
            model="chirp_3",
            location="asia-southeast1",
            enable_word_time_offsets=False,
            # Chirp 3 specific
            languages="th-TH",
            detect_language=False,
            use_streaming=use_streaming,
            denoiser_config=denoiser_config,
        )

    async def turn_detection(self) -> TurnDetectionMode | NotGiven:
        """TODO."""
        turn_detection_mode = await self._get_feature_value(
            key="livekit:turn_detection", fallback=NOT_GIVEN
        )
        if turn_detection_mode in ["stt", "vad", NOT_GIVEN]:
            return turn_detection_mode

        # EOU model hits get_job_context() on init, so they can't be prewarmed
        if turn_detection_mode == "EnglishModel":
            return EnglishModel()
        if turn_detection_mode == "MultilingualModel":
            return MultilingualModel()

        logger.error("TODO not supported turn detection mode: %s", turn_detection_mode)
        return NOT_GIVEN

    async def _get_feature_value(self, key: str, fallback: Any):
        # TODO typing with Pydantic
        return await self.growthbook.get_feature_value(
            key=key, fallback=fallback, user_context=self.user_context
        )


def _get_noise_cancellation(params: NoiseCancellationParams):
    return (
        noise_cancellation.BVCTelephony()
        if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
        else noise_cancellation.BVC()
    )
