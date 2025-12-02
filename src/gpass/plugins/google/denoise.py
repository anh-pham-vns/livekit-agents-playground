"""TODO."""

from enum import Enum

from google.cloud.speech_v2.types.cloud_speech import DenoiserConfig


class DenoiseProfile(Enum):
    """TODO."""

    # Denoise Enabled
    ON_HIGH = DenoiserConfig(denoise_audio=True, snr_threshold=10.0)
    ON_MEDIUM = DenoiserConfig(denoise_audio=True, snr_threshold=20.0)
    ON_LOW = DenoiserConfig(denoise_audio=True, snr_threshold=40.0)
    ON_VERY_LOW = DenoiserConfig(denoise_audio=True, snr_threshold=100.0)

    # Denoise Disabled
    OFF_HIGH = DenoiserConfig(denoise_audio=False, snr_threshold=0.5)
    OFF_MEDIUM = DenoiserConfig(denoise_audio=False, snr_threshold=1.0)
    OFF_LOW = DenoiserConfig(denoise_audio=False, snr_threshold=2.0)
    OFF_VERY_LOW = DenoiserConfig(denoise_audio=False, snr_threshold=5.0)
