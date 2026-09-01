FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml README.md ./
COPY src ./src
COPY data ./data
COPY outputs ./outputs

RUN uv sync --no-dev

CMD ["uv", "run", "python", "-m", "support_agent.cli"]
