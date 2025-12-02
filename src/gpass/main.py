"""TODO."""

from livekit import agents
from livekit.plugins import silero

server = agents.AgentServer()


def prewarm(proc: agents.JobProcess):
    """TODO."""
    proc.userdata[silero] = silero.VAD.load()


server.setup_fnc = prewarm


def main():
    """Main function."""
    agents.cli.run_app(server)


if __name__ == "__main__":
    main()
