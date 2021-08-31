# Welcome to Hue (http://gethue.com) Dockerfile

FROM ubuntu:20.04
LABEL description="Hue SQL Assistant - gethue.com"

ENV DEBIAN_FRONTEND=noninteractive

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
  python3.8-venv \
  python3.8-dev \
  python3.8-distutils \
  rsync \
  curl \
  sudo \
  git && \
  rm -rf /var/lib/apt/lists/*

ADD . /hue

RUN pip3 install --upgrade --no-cache-dir setuptools virtualenv pip && \
  curl -sL https://deb.nodesource.com/setup_14.x | sudo bash - && \
  apt-get install -y nodejs && \
  addgroup hue && \
  useradd -r -u 1001 -g hue hue && \
  chown -R hue /hue && \
  mkdir /hue/build && \
  chown -R hue /hue/build && \
  mkdir /usr/share/hue && \
  chown -R hue /usr/share/hue && \
  rm -r /hue/desktop/conf/* && \
  cp -r /hue/desktop/conf.dist/* /hue/desktop/conf/ && \
  cd /hue && \
  PREFIX=/usr/share PYTHON_VER=python3.8 make install && \
  chown -R hue /usr/share/hue && \
  npm cache clean --force && \
  pip cache purge && \
  rm -rf /var/lib/apt/lists/* && \
  cp -r /hue/tools/docker/hue/conf3/* /usr/share/hue/desktop/conf/ && \
  cp /hue/tools/docker/hue/startup.sh /usr/share/hue/startup.sh && \
  mkdir -p /usr/share/hue/tools/slack && \
  cp /hue/tools/slack/manifest.yml /usr/share/hue/tools/slack/manifest.yml && \
  rm -rf /hue && \
  rm -rf /usr/share/hue/node_modules

WORKDIR /usr/share/hue

# Install DB connectors
# To move to requirements_connectors.txt
RUN ./build/env/bin/pip install --no-cache-dir \
  psycopg2-binary \
  # Avoid Django 3 pulling
  django_redis==4.11.0 \
  flower==0.9.7 \
  # Contains fix for SparkSql show tables
  git+https://github.com/gethue/PyHive \
  # pyhive \
  impyla==0.17.0 \
  #ksql \
  git+https://github.com/bryanyang0528/ksql-python \
  pydruid \
  pybigquery \
  elasticsearch-dbapi \
  pyasn1==0.4.1 \
  # View some parquet files
  python-snappy==0.5.4 \
  # Needed for Jaeger
  threadloop \
  # Fix Can't load plugin: sqlalchemy.dialects:clickhouse
  sqlalchemy-clickhouse \
  # sqlalchemy-clickhouse depend on infi.clickhouse_orm
  # install after sqlalchemy-clickhouse and version == 1.0.4
  # otherwise Code: 516, Authentication failed will display
  infi.clickhouse_orm==1.0.4

USER hue

EXPOSE 8888

CMD ["./startup.sh"]
