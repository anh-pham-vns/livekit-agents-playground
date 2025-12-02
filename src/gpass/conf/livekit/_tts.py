"""TODO."""

from enum import StrEnum, auto

from hydra_zen.typing import Builds

from gpass.plugins.google import SegmentedTokenizer
from livekit.agents import tts
from livekit.plugins import google

from ._common import builds


class Provider(StrEnum):
    Chirp_3 = auto()


Google = builds(
    google.TTS, language="th-TH", tokenizer=builds(SegmentedTokenizer, bytes_limit=900)
)

# Chirp3 TTS is compulsory, now we don't have fallback
REGISTRY: dict[Provider, Builds[type[tts.TTS]]] = {
    Provider.Chirp_3: Google(
        voice_name="th-TH-Chirp3-HD-Autonoe", speaking_rate=1.2, use_markup=True
    )
}
