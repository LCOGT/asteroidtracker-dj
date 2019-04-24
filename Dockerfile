FROM python:3.6-alpine

ENV PYTHONUNBUFFERED 1
ENV C_FORCE_ROOT true

# set working directory
WORKDIR /var/www/apps/asteroidday

# install depedencies
COPY requirements.txt .
RUN apk --no-cache add libjpeg-turbo mariadb-connector-c zlib libgomp ffmpeg \
        && apk --no-cache add --virtual .build-deps gcc g++ git mariadb-dev musl-dev zlib-dev \
        && pip --no-cache-dir --trusted-host=buildsba.lco.gtn install -r requirements.txt \
        && apk --no-cache del .build-deps

# install application
COPY app .
