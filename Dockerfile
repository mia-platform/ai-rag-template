FROM python:3.13.0-slim

RUN useradd -s /bin/bash python

EXPOSE 3000
WORKDIR /app

ADD  . /app

RUN pip install --upgrade pip 
RUN pip install -r requirements.txt

ARG COMMIT_SHA=<not-specified>
RUN echo "ai-rag-template: $COMMIT_SHA" >> ./commit.sha

LABEL maintainer="%CUSTOM_PLUGIN_CREATOR_USERNAME%" \
      name="ai-rag-template" \
      description="%CUSTOM_PLUGIN_SERVICE_DESCRIPTION%" \
      eu.mia-platform.url="https://www.mia-platform.eu" \
      eu.mia-platform.version="0.5.3"

USER python

CMD ["python", "-m", "src.app"]