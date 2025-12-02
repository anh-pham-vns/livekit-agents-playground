"""TODO."""

from livekit import agents


class Assistant(agents.Agent):
    """TODO."""

    def __init__(self) -> None:
        """TODO."""
        super().__init__(instructions="You are a voice bot, your input is user speech")
