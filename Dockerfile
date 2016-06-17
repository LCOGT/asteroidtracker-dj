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
  && yum -y install ImageMagick \
	&& yum -y install autoconf automake gcc gcc-c++ git libtool make  nasm pkgconfig zlib-devel \
	&& yum -y update

# Compile FFMPEG and libraries
RUN mkdir ~/ffmpeg_sources && cd ~/ffmpeg_sources \
	&& git clone --depth 1 git://git.videolan.org/x264 \
	&& cd x264 \
	&& PKG_CONFIG_PATH="$HOME/ffmpeg_build/lib/pkgconfig" ./configure --prefix="$HOME/ffmpeg_build" --bindir="$HOME/bin" --enable-static --disable-asm \
	&& make \
	&& make install \
	&& make distclean \
	&& cd ~/ffmpeg_sources \
	&& curl -L -O http://downloads.sourceforge.net/project/lame/lame/3.99/lame-3.99.5.tar.gz \
	&& tar xzvf lame-3.99.5.tar.gz \
	&& cd lame-3.99.5 \
	&& ./configure --prefix="$HOME/ffmpeg_build" --bindir="$HOME/bin" --disable-shared --enable-nasm \
	&& make \
	&& make install \
	&& make distclean \
	&& cd ~/ffmpeg_sources \
	&& git clone https://git.ffmpeg.org/ffmpeg.git ffmpeg \
	&& cd ffmpeg \
	&& PKG_CONFIG_PATH="$HOME/ffmpeg_build/lib/pkgconfig" ./configure --prefix="$HOME/ffmpeg_build" --extra-cflags="-I$HOME/ffmpeg_build/include" --extra-ldflags="-L$HOME/ffmpeg_build/lib" --bindir="$HOME/bin" --pkg-config-flags="--static" --enable-gpl --enable-libmp3lame --enable-libx264\
	&& make \
	&& make install \
	&& make distclean \
	&& hash -r

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
