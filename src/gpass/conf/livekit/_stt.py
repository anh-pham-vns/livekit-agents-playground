import logging
import os
from enum import StrEnum, auto

from hydra_zen.typing import Builds

from livekit.agents import stt
from livekit.plugins import aws, google

from ._common import builds

logger = logging.getLogger(__name__)


class Provider(StrEnum):
    Transcribe = auto()
    Chirp_3 = auto()


AWS = builds(aws.STT, language="th-TH")
Google = builds(
    google.STT, languages="th-TH", detect_language=False, use_streaming=False
)

REGISTRY: dict[Provider, Builds[type[stt.STT]]] = {
    Provider.Transcribe: AWS(),
}

if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
    REGISTRY[Provider.Chirp_3] = Google(
        model="chirp_3", enable_word_time_offsets=False, location="asia-southeast1"
    )
