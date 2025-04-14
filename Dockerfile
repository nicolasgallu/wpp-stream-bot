FROM python:3.12-slim

WORKDIR /usr/src/app

# 1. install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. copy your source code
COPY app ./app

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/usr/src/app

# Docker Compose will choose the entrypoint,
# so we leave CMD/ENTRYPOINT empty here.
