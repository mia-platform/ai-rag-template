FROM python:3.12.3-slim

RUN useradd -s /bin/bash python

EXPOSE 3000
WORKDIR /app

ADD  . /app

RUN pip install --upgrade pip 
RUN pip install -r requirements.txt

ARG COMMIT_SHA=<not-specified>
RUN echo "ai-rag-template: $COMMIT_SHA" >> ./commit.sha

LABEL maintainer="alessio.bernardi@cnh.com" \
      name="ai-rag-template" \
      description="" \
      eu.mia-platform.url="https://www.mia-platform.eu" \
      eu.mia-platform.version="0.3.1"

USER python

CMD ["python", "-m", "src.app"]