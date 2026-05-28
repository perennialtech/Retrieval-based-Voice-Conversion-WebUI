# syntax=docker/dockerfile:1

FROM nvidia/cuda:12.8.0-cudnn-runtime-ubuntu22.04

COPY --from=ghcr.io/astral-sh/uv:0.11.16 /uv /uvx /usr/local/bin/

EXPOSE 7865

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/app/.venv/bin:${PATH}"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        aria2 \
        build-essential \
        git \
        python3.12 \
        python3.12-dev \
        python3.12-venv && \
    rm -rf /var/lib/apt/lists/*

COPY . .

RUN rm -rf .venv && \
    uv sync --python python3.12 --extra cuda

RUN aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/fumiama/RVC-Pretrained-Models/resolve/main/pretrained_v2/D40k.pth -d assets/pretrained_v2/ -o D40k.pth
RUN aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/fumiama/RVC-Pretrained-Models/resolve/main/pretrained_v2/G40k.pth -d assets/pretrained_v2/ -o G40k.pth
RUN aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/fumiama/RVC-Pretrained-Models/resolve/main/pretrained_v2/f0D40k.pth -d assets/pretrained_v2/ -o f0D40k.pth
RUN aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/fumiama/RVC-Pretrained-Models/resolve/main/pretrained_v2/f0G40k.pth -d assets/pretrained_v2/ -o f0G40k.pth

RUN aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/fumiama/RVC-Pretrained-Models/resolve/main/uvr5_weights/HP2-人声vocals+非人声instrumentals.pth -d assets/uvr5_weights/ -o HP2-人声vocals+非人声instrumentals.pth
RUN aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/fumiama/RVC-Pretrained-Models/resolve/main/uvr5_weights/HP5-主旋律人声vocals+其他instrumentals.pth -d assets/uvr5_weights/ -o HP5-主旋律人声vocals+其他instrumentals.pth

RUN aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/fumiama/RVC-Pretrained-Models/resolve/main/hubert/hubert_base.pt -d assets/hubert -o hubert_base.pt

RUN aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/fumiama/RVC-Pretrained-Models/resolve/main/rmvpe/rmvpe.pt -d assets/rmvpe -o rmvpe.pt

VOLUME [ "/app/weights", "/app/opt" ]

CMD ["python", "web.py"]
