# syntax=docker/dockerfile:1.7

FROM nvidia/cuda:12.9.2-cudnn-runtime-ubuntu24.04

COPY --from=ghcr.io/astral-sh/uv:0.11.16 /uv /uvx /usr/local/bin/

ARG DEBIAN_FRONTEND=noninteractive

# Space-separated extras.
# Examples:
#   --build-arg RVC_EXTRAS="cuda"
#   --build-arg RVC_EXTRAS="cuda gui"
#   --build-arg RVC_EXTRAS="cpu"
ARG RVC_EXTRAS="cuda"

# Set to 0 if you want a smaller image and prefer runtime downloads.
ARG DOWNLOAD_MODELS=1

ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
  UV_PYTHON_INSTALL_DIR=/opt/uv-python \
  UV_LINK_MODE=copy \
  UV_COMPILE_BYTECODE=1 \
  UV_NO_PROGRESS=1 \
  VIRTUAL_ENV=/opt/venv \
  PATH="/opt/venv/bin:${PATH}" \
  PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  NVIDIA_VISIBLE_DEVICES=all \
  NVIDIA_DRIVER_CAPABILITIES=compute,utility

WORKDIR /app

RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  aria2 \
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

# Download model assets before copying the full source tree so normal code
# changes do not invalidate these large layers.
RUN if [ "${DOWNLOAD_MODELS}" = "1" ]; then \
  set -eux; \
  download() { \
  url="$1"; \
  dir="$2"; \
  out="$3"; \
  mkdir -p "${dir}"; \
  aria2c \
  --console-log-level=warn \
  --summary-interval=0 \
  --continue=true \
  --max-connection-per-server=16 \
  --split=16 \
  --min-split-size=1M \
  --max-tries=5 \
  --retry-wait=5 \
  "${url}" \
  -d "${dir}" \
  -o "${out}"; \
  }; \
  download "https://huggingface.co/fumiama/RVC-Pretrained-Models/resolve/main/pretrained_v2/D40k.pth" \
  "assets/pretrained_v2" \
  "D40k.pth"; \
  download "https://huggingface.co/fumiama/RVC-Pretrained-Models/resolve/main/pretrained_v2/G40k.pth" \
  "assets/pretrained_v2" \
  "G40k.pth"; \
  download "https://huggingface.co/fumiama/RVC-Pretrained-Models/resolve/main/pretrained_v2/f0D40k.pth" \
  "assets/pretrained_v2" \
  "f0D40k.pth"; \
  download "https://huggingface.co/fumiama/RVC-Pretrained-Models/resolve/main/pretrained_v2/f0G40k.pth" \
  "assets/pretrained_v2" \
  "f0G40k.pth"; \
  download "https://huggingface.co/fumiama/RVC-Pretrained-Models/resolve/main/uvr5_weights/HP2-人声vocals+非人声instrumentals.pth" \
  "assets/uvr5_weights" \
  "HP2-人声vocals+非人声instrumentals.pth"; \
  download "https://huggingface.co/fumiama/RVC-Pretrained-Models/resolve/main/uvr5_weights/HP5-主旋律人声vocals+其他instrumentals.pth" \
  "assets/uvr5_weights" \
  "HP5-主旋律人声vocals+其他instrumentals.pth"; \
  download "https://huggingface.co/fumiama/RVC-Pretrained-Models/resolve/main/hubert/hubert_base.pt" \
  "assets/hubert" \
  "hubert_base.pt"; \
  download "https://huggingface.co/fumiama/RVC-Pretrained-Models/resolve/main/rmvpe/rmvpe.pt" \
  "assets/rmvpe" \
  "rmvpe.pt"; \
  fi

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
  ${extra_flags}

VOLUME ["/app/weights", "/app/opt"]

CMD ["python", "web.py", "--listen", "--noautoopen"]
