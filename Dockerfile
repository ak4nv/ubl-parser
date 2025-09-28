# Base
FROM python:3.12-slim AS base

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    uv sync

ENV PATH="/app/.venv/bin:$PATH"

COPY app/ /app/src

CMD ["fastapi", "run", "src/main.py", "--port", "80"]
