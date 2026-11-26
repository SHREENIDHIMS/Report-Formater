FROM python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b

ARG LIBREOFFICE_VERSION=4:25.2.3-2+deb13u12
ARG FONTS_DEJAVU_VERSION=2.37-8
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libreoffice-writer=${LIBREOFFICE_VERSION} \
        fonts-dejavu=${FONTS_DEJAVU_VERSION} \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /worker
COPY pyproject.toml uv.lock /worker/
RUN pip install --no-cache-dir uv && uv sync --frozen --no-dev
COPY app /worker/app
COPY worker/rendering/entrypoint.py /worker/entrypoint.py

RUN useradd --system --uid 10001 worker \
    && mkdir -p /work \
    && chown -R worker:worker /worker /work
USER worker
ENV HOME=/work PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ENTRYPOINT ["/worker/.venv/bin/python", "/worker/entrypoint.py"]
