# syntax = docker/dockerfile:1.0-experimental
FROM python:3-alpine

RUN mkdir /app
WORKDIR /app

RUN apk add gcc musl-dev libffi-dev postgresql-dev libmemcached-dev zlib-dev make

COPY ./requirements.txt /app/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

COPY . .

EXPOSE 8000
