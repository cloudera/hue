# Welcome to Hue (http://gethue.com) Dockerfile

FROM ubuntu:18.04
LABEL description="Hue SQL Assistant - gethue.com"

# TODO: run as hue from the start to avoid the long chmod

ENV DEBIAN_FRONTEND=noninteractive
RUN export PYTHON_VER=python3.6

RUN apt-get update -y && apt-get install -y \
  python3-pip \
  #libmariadb-dev-compat \
  # python3.6-dev \

  #libsasl2-modules-gssapi-mit \
  libkrb5-dev \
  libsasl2-dev \
  libxml2-dev \
  libxslt-dev \
  #libssl-dev \
  libmysqlclient-dev \
  libldap2-dev \
  libsnappy-dev \
  python3.6-venv

ADD . /hue
WORKDIR /hue

RUN pip3 install virtualenv
RUN python3.6 -m venv python_env

SHELL ["/bin/bash", "-c"]
RUN source python_env/bin/activate

RUN pip3 install -r desktop/core/requirements.txt


# Not doing a `make prod`, so manually getting production ini
RUN rm desktop/conf/*
COPY desktop/conf.dist desktop/conf

# Need recent version for Ubuntu
# RUN curl -sL https://deb.nodesource.com/setup_10.x | sudo bash - \
#  && apt-get install -y nodejs

RUN PREFIX=/usr/share PYTHON_VER=python3.6 make install # install not working?
RUN useradd -ms /bin/bash hue && chown -R hue /usr/share/hue

# Only keep install dir
# Note: get more minimal image by pulling install dir in a stage 2 image
WORKDIR /usr/share/hue
RUN rm -rf /hue \
  && rm -rf node_modules

# Install DB connectors
# To move to requirements_connectors.txt
RUN ./build/env/bin/pip install \
  psycopg2-binary \
  redis==2.10.6 \
  django_redis \
  flower \
  pyhive \
  gevent \
  # Needed for Jaeger
  threadloop \
  thrift-sasl==0.2.1

COPY tools/docker/hue/conf desktop/conf
COPY tools/docker/hue/startup.sh .

EXPOSE 8888
CMD ["./startup.sh"]
