# syntax=docker/dockerfile:1.7

ARG BASE_IMAGE=nvidia/cuda:12.9.2-cudnn-runtime-ubuntu24.04
FROM ${BASE_IMAGE}

COPY --from=ghcr.io/astral-sh/uv:0.11.16 /uv /uvx /usr/local/bin/

ARG DEBIAN_FRONTEND=noninteractive

# Space-separated extras.
# Examples:
#   --build-arg RVC_EXTRAS="cuda"
#   --build-arg RVC_EXTRAS="cuda gui"
#   --build-arg RVC_EXTRAS="cpu"
ARG RVC_EXTRAS="cuda"

ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON_INSTALL_DIR=/opt/uv-python \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_PROGRESS=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        ffmpeg \
        git \
        libgomp1 \
        libsndfile1 \
        pkg-config && \
    rm -rf /var/lib/apt/lists/*

# Copy only dependency metadata first for better Docker cache reuse.
COPY .python-version pyproject.toml uv.lock README.md LICENSE ./

# Install Python and third-party dependencies, but not the project yet.
RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    set -eux; \
    uv python install "$(cat .python-version)"; \
    extra_flags=""; \
    for extra in ${RVC_EXTRAS}; do \
        extra_flags="${extra_flags} --extra ${extra}"; \
    done; \
    uv sync \
        --locked \
        --python "$(cat .python-version)" \
        --no-dev \
        --no-install-project \
        ${extra_flags}

# Now copy the actual app.
COPY . .

# Install the project itself.
RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    set -eux; \
    extra_flags=""; \
    for extra in ${RVC_EXTRAS}; do \
        extra_flags="${extra_flags} --extra ${extra}"; \
    done; \
    uv sync \
        --locked \
        --python "$(cat .python-version)" \
        --no-dev \
        --no-editable \
        ${extra_flags}; \
    mkdir -p assets logs opt

EXPOSE 7865

CMD ["python", "web.py", "--listen", "--noautoopen", "--update"]
