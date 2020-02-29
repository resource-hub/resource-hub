FROM python:3-alpine

ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache linux-headers bash gcc \
    musl-dev libjpeg-turbo-dev libpng \
    postgresql-dev git zlib-dev libmagic \
    gettext graphviz libffi-dev

WORKDIR /site
COPY ./ /site
RUN pip3 install -r requirements.txt 
