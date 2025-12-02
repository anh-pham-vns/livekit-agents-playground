FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim AS builder
# https://docs.astral.sh/uv/guides/integration/docker/#caching
ENV UV_LINK_MODE=copy 
# No downloads needed, final stage uses system Python
ENV UV_PYTHON_DOWNLOADS=0
# Use lock file for reproducible builds
ENV UV_LOCKED=1
# Skip development dependencies
ENV UV_NO_DEV=1
# Non-editable installs for production deployment
ENV UV_NO_EDITABLE=1

RUN apt-get update && apt-get install --yes --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock,readonly \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml,readonly \
    uv sync --no-install-project

COPY README.md ./
COPY src/ ./src/
# Mount .git for dynamic versioning with scm
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock,readonly \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml,readonly \
    --mount=type=bind,source=.git,target=.git,readonly \
    uv sync 

FROM docker.io/python:3.13-slim-trixie
# https://www.fourdigits.nl/blog/python-containers-best-practices/
ENV PYTHONUNBUFFERED=1

# For torchcodec inside pyannote.audio
RUN apt-get update && apt-get install --yes --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/.venv /app/.venv

WORKDIR /app

ENV LOG_LEVEL=info
ENTRYPOINT ["/app/.venv/bin/python", "-m", "gpass.agent"]
CMD ["start"]
# https://docs.livekit.io/agents/v0/deployment/#networking
HEALTHCHECK CMD bash -c '</dev/tcp/localhost/8081' || exit 1
