FROM python:3.6-alpine
MAINTAINER LCOGT <webmaster@lcogt.net>

EXPOSE 80

ENV PYTHONUNBUFFERED 1
ENV C_FORCE_ROOT true

# install depedencies
COPY requirements.pip /var/www/apps/asteroidday/
RUN apk --no-cache add mariadb-client-libs \
        && apk --no-cache add --virtual .build-deps gcc git mariadb-dev musl-dev \
        && apk --no-cache add libjpeg-turbo jpeg-dev libjpeg libjpeg-turbo-dev imagemagick zlib zlib-dev ffmpeg \
        && pip --no-cache-dir --trusted-host=buildsba.lco.gtn install -r /var/www/apps/asteroidday/requirements.pip \
        && apk --no-cache del .build-deps

# install entrypoint
COPY docker/ /

# Ensure crond will run on all host operating systems
RUN crontab /crontab.root \
    && rm -rf /crontab.root

# install web application
COPY app /var/www/apps/asteroidday/
ENTRYPOINT [ "/init" ]
