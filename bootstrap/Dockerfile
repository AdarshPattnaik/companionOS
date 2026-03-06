FROM python:3.11-slim-bullseye

LABEL maintainer="Coratia <dev@coratia.com>"
LABEL description="CoratiaOS Bootstrap — Core container lifecycle manager"

RUN pip install --no-cache-dir docker requests

COPY . /bootstrap
WORKDIR /bootstrap

ENTRYPOINT ["python", "main.py"]
