"""TODO."""

import logging

from livekit import agents
from livekit.agents import room_io
from livekit.plugins import groq, silero

from gpass.agents.default import Assistant
from gpass.schema import LKUserData
from gpass.services import livekit

logger = logging.getLogger(__name__)


agent_server = agents.AgentServer()


@agent_server.rtc_session()
async def default_agent(ctx: agents.JobContext):
    """TODO."""
    await ctx.connect(auto_subscribe=agents.AutoSubscribe.AUDIO_ONLY)

    session = agents.AgentSession(
        turn_detection="vad",
        stt=groq.STT(model="whisper-large-v3-turbo", detect_language=True),
        llm=groq.LLM(model="llama-3.3-70b-versatile"),
        tts=groq.TTS(model="playai-tts"),
        vad=silero.VAD.load(),
        userdata=LKUserData(),
    )

    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=livekit._noise_cancellation_selector
            ),
            delete_room_on_close=True,
        ),
        record=False,
    )
