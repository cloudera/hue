# Welcome to Hue (http://gethue.com) Dockerfile

FROM ubuntu:18.04
LABEL description="Hue SQL Assistant - gethue.com"

RUN apt-get update -y && apt-get install -y \
  python3-pip \
  libkrb5-dev  \
  libsasl2-modules-gssapi-mit \
  libsasl2-dev \
  libkrb5-dev \
  libxml2-dev \
  libxslt-dev \
  libmysqlclient-dev \
  libldap2-dev \
  libsnappy-dev \
  python3.6-venv \
  rsync \
  curl \
  sudo \
  git

RUN pip3 install --upgrade setuptools
RUN pip3 install virtualenv

# Need recent version for Ubuntu
RUN curl -sL https://deb.nodesource.com/setup_10.x | sudo bash - \
  && apt-get install -y nodejs

RUN addgroup hue && useradd -r -u 1001 -g hue hue

ADD . /hue
WORKDIR /hue

RUN chown -R hue /hue \
  && mkdir /hue/build \
  && chown -R hue /hue/build \
  && mkdir /usr/share/hue \
  && chown -R hue /usr/share/hue

# Not doing a `make prod`, so manually getting production ini
RUN rm desktop/conf/*
COPY desktop/conf.dist desktop/conf

RUN rm -r desktop/core/ext-py

RUN PREFIX=/usr/share PYTHON_VER=python3.6 make install
RUN chown -R hue /usr/share/hue

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
  # Avoid Django 3 pulling
  django_redis==4.11.0 \
  flower \
  # SparkSql show tables
  git+https://github.com/gethue/PyHive \
  # pyhive \
  ksql \
  pydruid \
  pybigquery \
  elasticsearch-dbapi \
  pyasn1==0.4.1 \
  # View some parquet files
  python-snappy==0.5.4 \
  threadloop  # Needed for Jaeger \
  thrift-sasl==0.2.1


COPY tools/docker/hue/conf3 desktop/conf
COPY tools/docker/hue/startup.sh .

USER hue

EXPOSE 8888
CMD ["./startup.sh"]
