FROM python:3.8.1-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && apk upgrade && apk add --no-cache bash

WORKDIR /app

COPY wait-for-it.sh ./

COPY Pipfile Pipfile.lock ./

RUN set -ex \
    && apk update \
    && apk upgrade \
    && apk add --no-cache --virtual .build-deps \
    gcc \
    postgresql-dev \
    libc-dev \
    musl-dev \
    openssl-dev \
    libffi-dev \
    && pip install --upgrade pip \
    && pip install pipenv==2018.11.26 \
    && pipenv install --system --dev --deploy \
    && runDeps="$( \
            scanelf --needed --nobanner --recursive /usr/local \
                    | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
                    | sort -u \
                    | xargs -r apk info --installed \
                    | sort -u \
    )" \
    && apk add --virtual .python-rundeps $runDeps \
    && apk del .build-deps

COPY . .

CMD ["python manage.py start"]
