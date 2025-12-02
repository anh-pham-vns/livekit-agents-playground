from enum import StrEnum, auto

from hydra_zen.typing import Builds

from livekit.agents import llm
from livekit.agents.types import NOT_GIVEN
from livekit.plugins import aws, google

from ._common import builds


class Provider(StrEnum):
    Sonnet_4_0 = auto()
    Sonnet_4_5 = auto()
    Gemini_2_5_Flash = auto()


Bedrock = builds(aws.LLM, region=NOT_GIVEN, temperature=0.1, max_output_tokens=2000)
Gemini = builds(google.LLM, temperature=0.1, max_output_tokens=3000)


REGISTRY: dict[Provider, Builds[type[llm.LLM]]] = {
    Provider.Sonnet_4_0: Bedrock(model="apac.anthropic.claude-sonnet-4-20250514-v1:0"),
    Provider.Sonnet_4_5: Bedrock(
        model="global.anthropic.claude-sonnet-4-5-20250929-v1:0"
    ),
}
