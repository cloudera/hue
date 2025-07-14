# Welcome to Hue (http://gethue.com) Dockerfile

FROM ubuntu:22.04
LABEL description="Hue SQL Assistant - gethue.com"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y && apt-get install -y \
  python3.11 \
  python3.11-venv \
  python3.11-dev \
  python3.11-distutils \
  python3-pip \
  libkrb5-dev  \
  libsasl2-modules-gssapi-mit \
  libsasl2-dev \
  krb5-config \
  krb5-user \
  libxml2-dev \
  libxslt-dev \
  libmysqlclient-dev \
  libldap2-dev \
  libsnappy-dev \
  libffi-dev \
  pkg-config \
  rsync \
  curl \
  sudo \
  git && \
  rm -rf /var/lib/apt/lists/*

ADD . /hue

RUN pip3 install --upgrade --no-cache-dir setuptools virtualenv pip && \
  apt-get install -y curl && \
  curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
  apt-get install -y nodejs && \
  addgroup hue && \
  useradd -r -u 1001 -g hue hue && \
  chown -R hue /hue && \
  mkdir /hue/build && \
  chown -R hue /hue/build && \
  mkdir /usr/share/hue && \
  chown -R hue /usr/share/hue && \
  rm -rf /hue/desktop/conf && \
  cp -r /hue/desktop/conf.dist /hue/desktop/conf && \
  mkdir -m 755 /var/log/hue && \
  cd /hue && \
  ln -fs /usr/local/bin/pip3.11 /usr/bin/pip3.11 && \
  ln -fs /usr/local/bin/pip3.11 /usr/bin/pip3 && \
  PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python \
  PREFIX=/usr/share INSTALL_DIR=/usr/share/hue ROOT=/usr/share/hue PYTHON_VER=python3.11 \
  SYS_PYTHON=/usr/bin/python3.11 SYS_PIP=/usr/local/bin/pip3.11 make apps install && \
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
  # Avoid Django 3 pulling \
  django_redis==5.4.0 \
  flower==2.0.1 \
  # Contains fix for SparkSql show tables \
  git+https://github.com/gethue/PyHive \
  #ksql \
  git+https://github.com/bryanyang0528/ksql-python \
  pydruid \
  # pybigquery \
  elasticsearch-dbapi \
  pyasn1==0.6.1 \
  # View some parquet files \
  python-snappy==0.7.3 \
  # Needed for Jaeger \
  threadloop \
  # Fix Can't load plugin: sqlalchemy.dialects:clickhouse \
  sqlalchemy-clickhouse \
  # sqlalchemy-clickhouse depend on infi.clickhouse_orm \
  # install after sqlalchemy-clickhouse and version == 1.0.4 \
  # otherwise Code: 516, Authentication failed will display \
  infi.clickhouse_orm==1.0.4 \
  mysqlclient==2.2.7 \
  PyAthena==3.14.1

USER hue

EXPOSE 8888

CMD ["./startup.sh"]
