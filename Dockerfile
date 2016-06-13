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
	&& yum -y install cronie libjpeg-devel nginx python-pip mysql-devel python-devel \
  && yum -y install supervisor libssl \
	&& yum -y groupinstall "Development Tools"\
  && yum -y install ImageMagick ffmpeg \
	&& yum -y update

# Copy the LCOGT Mezzanine webapp files
COPY app/requirements.pip /var/www/apps/asteroidday/requirements.pip

RUN pip install pip==1.3 && pip install uwsgi==2.0.8 \
		&& pip install -r /var/www/apps/asteroidday/requirements.pip

# Setup the Python Django environment
ENV PYTHONPATH /var/www/apps
ENV DJANGO_SETTINGS_MODULE asteroidday.settings

# Ensure crond will run on all host operating systems
RUN sed -i -e 's/\(session\s*required\s*pam_loginuid.so\)/#\1/' /etc/pam.d/crond

# Copy configuration files
COPY config/uwsgi.ini /etc/uwsgi.ini
COPY config/nginx/* /etc/nginx/
COPY config/processes.ini /etc/supervisord.d/processes.ini

# Copy configuration files
COPY config/init /init

# Copy the LCOGT Asteroid Day files
COPY app /var/www/apps/asteroidday
