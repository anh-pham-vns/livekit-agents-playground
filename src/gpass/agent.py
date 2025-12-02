"""TODO."""

import logging

from livekit import agents
from livekit.agents import Agent, AgentServer, AgentSession, room_io, vad
from livekit.plugins import silero

from gpass.deps import Container
from gpass.schema import LKUserData

logger = logging.getLogger(__name__)


class Assistant(Agent):
    """TODO."""

    def __init__(self) -> None:
        """TODO."""
        super().__init__(instructions="Nothing")


server = AgentServer()


def prewarm(proc: agents.JobProcess):
    """TODO."""
    proc.userdata[vad] = silero.VAD.load()


server.setup_fnc = prewarm


async def on_request(req: agents.JobRequest):
    """TODO."""


async def on_session_end(ctx: agents.JobContext) -> None:
    """TODO."""
    _ = ctx.make_session_report()


# @server.rtc_session(on_request=on_request, on_session_end=on_session_end)
async def my_agent(ctx: agents.JobContext):
    """TODO."""
    container = Container()
    lk_provider = await container.lk_provider.async_()

    await ctx.connect(auto_subscribe=agents.AutoSubscribe.AUDIO_ONLY)

    session = AgentSession(
        turn_detection=await lk_provider.turn_detection(),
        stt=await lk_provider.stt(),
        vad=ctx.proc.userdata[vad],
        userdata=LKUserData(),
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=await lk_provider.noise_cancellation(),
            ),
            delete_room_on_close=True,
        ),
        record=await lk_provider.record_enabled(),
    )


def main():
    """Main function."""
    agents.cli.run_app(server)


if __name__ == "__main__":
    main()
