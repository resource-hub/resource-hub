FROM python:3.7-alpine

ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache linux-headers bash gcc \
    musl-dev libjpeg-turbo-dev libpng libpq \
    postgresql-dev uwsgi uwsgi-python3 git \
    zlib-dev libmagic

WORKDIR /site
COPY ./ /site
RUN pip install -U -r /site/requirements.txt
CMD cd src && python manage.py migrate && uwsgi --ini=/site/uwsgi.ini
