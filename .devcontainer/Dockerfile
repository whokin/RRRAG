FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

# uv — the project's package manager (ADR-0003); via PyPI, ghcr.io pulls
# time out on some networks
RUN pip install --no-cache-dir uv

# rclone — data/ <-> private R2 bucket (ADR-0001, ADR-0004). The base image
# ships a yarn apt repo with an expired key; drop it before updating.
RUN rm -f /etc/apt/sources.list.d/yarn.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends rclone \
    && rm -rf /var/lib/apt/lists/*
