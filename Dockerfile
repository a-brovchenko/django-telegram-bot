FROM python:3.10.12-alpine3.18

WORKDIR /app

RUN \
    apk update && \
    apk add --virtual build-deps gcc python3-dev musl-dev && \
    apk add --no-cache mariadb-dev &&\
    apk add --no-cache chromium chromium-chromedriver

COPY app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apk del build-deps

COPY app/ ./

WORKDIR /app/web

ENV DJANGO_SETTINGS_MODULE="web.settings" 

EXPOSE 8090

ENTRYPOINT \
    python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py runserver 0.0.0.0:8090