"""TODO."""

import os

from livekit import agents

from gpass.rtc_session import default, stt_playground


def main():
    """Main function."""
    mode = os.getenv("AGENT_MODE", "default")
    agent_server = (
        stt_playground.agent_server
        if mode == "stt_playground"
        else default.agent_server
    )
    agents.cli.run_app(agent_server)


if __name__ == "__main__":
    main()
