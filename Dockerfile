FROM python:3.13.18-slim-trixie

RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

# Upgrade the pip bundled with the system Python (vendored msgpack/urllib3 CVEs)
RUN python -m pip install --no-cache-dir --root-user-action=ignore --upgrade pip

RUN useradd -s /bin/bash python

EXPOSE 3000
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ADD  . /app

# Install dependencies using uv
RUN uv sync --frozen --no-cache

ARG COMMIT_SHA=<not-specified>
RUN echo "ai-rag-template: $COMMIT_SHA" >> ./commit.sha

LABEL maintainer="%CUSTOM_PLUGIN_CREATOR_USERNAME%" \
      name="ai-rag-template" \
      description="%CUSTOM_PLUGIN_SERVICE_DESCRIPTION%" \
      eu.mia-platform.url="https://www.mia-platform.eu" \
      eu.mia-platform.version="0.6.0"

USER python

CMD ["uv", "run", "python", "-m", "src.app"]
