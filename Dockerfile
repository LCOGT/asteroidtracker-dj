################################################################################
#
# Runs the LCOGT Asteroid Day app using nginx + uwsgi
#
# Build with
# docker build -t docker.lcogt.net/asteroidday:latest .
#
# Push to docker registry with
# docker push docker.lcogt.net/asteroidday:latest
#
################################################################################
FROM centos:centos7
MAINTAINER LCOGT <webmaster@lcogt.net>

# nginx (http protocol) runs on port 80
EXPOSE 80
ENTRYPOINT [ "/init" ]

# Setup the Python Django environment
ENV PYTHONPATH /var/www/apps
ENV DJANGO_SETTINGS_MODULE asteroidday.settings

# Install package repositories
RUN yum -y install epel-release \
	&& yum -y install http://li.nux.ro/download/nux/dextop/el7/x86_64/nux-dextop-release-0-1.el7.nux.noarch.rpm \
	&& yum -y install cronie ffmpeg gcc make libjpeg-devel nginx python-pip mysql-devel python-devel \
  && yum -y install supervisor libssl \
	&& yum -y groupinstall "Development Tools"\
  && yum -y install ImageMagick \
	&& yum -y update

# Copy the LCOGT Asteroid Day requirements file
COPY app/requirements.pip /var/www/apps/asteroidday/requirements.pip

RUN pip install -r /var/www/apps/asteroidday/requirements.pip

# Setup the Python Django environment
ENV PYTHONPATH /var/www/apps
ENV DJANGO_SETTINGS_MODULE asteroidday.settings

# Ensure crond will run on all host operating systems
RUN sed -i -e 's/\(session\s*required\s*pam_loginuid.so\)/#\1/' /etc/pam.d/crond

# Copy configuration files
COPY config/uwsgi.ini /etc/uwsgi.ini
COPY config/nginx/* /etc/nginx/
COPY config/processes.ini /etc/supervisord.d/processes.ini
COPY config/crontab.root /var/spool/cron/root

# Copy configuration files
COPY config/init /init

# Copy the LCOGT Asteroid Day files
COPY app /var/www/apps/asteroidday
