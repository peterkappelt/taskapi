FROM python:3.11-alpine AS builder

EXPOSE 8000
WORKDIR /app

RUN addgroup -S app && adduser -S app -G app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk add --update alpine-sdk libffi-dev postgresql-libs
# required for psycopg
RUN apk add --no-cache postgresql-dev musl-dev

COPY requirements.txt /app
RUN pip3 install -r requirements.txt --no-cache-dir
RUN pip3 install gunicorn
RUN pip3 install psycopg2
COPY . /app

RUN chown -R app:app /app
USER app
