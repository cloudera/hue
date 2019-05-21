# Welcome to Hue (http://gethue.com) Dockerfile
# Build an image from a remote github or local cloned Hue repository.

FROM ubuntu:18.04
LABEL description="Hue Project https://github.com/cloudera/hue"

RUN apt-get update -y && apt-get install -y \
  build-essential \
  libkrb5-dev \
  libmysqlclient-dev \
  libssl-dev \
  libsasl2-dev \
  libsasl2-modules-gssapi-mit \
  libsqlite3-dev \
  libtidy-dev \
  libxml2-dev \
  libxslt-dev \
  libffi-dev \
  libldap2-dev \
  libpq-dev \
  python-dev \
  python-setuptools \
  libgmp3-dev \
  libz-dev \
  software-properties-common \
  curl \
  git \
  rsync \
  sudo \
  maven \
  gcc \
  swig \
  openssl \
  xmlsec1 \
  libxmlsec1-openssl \
  hugo \
   && rm -rf /var/lib/apt/lists/*

ADD . /hue
WORKDIR /hue

# Not doing a `make prod`, so manually getting production ini
RUN rm desktop/conf/*
COPY desktop/conf.dist desktop/conf

# Need recent version for Ubuntu
RUN curl -sL https://deb.nodesource.com/setup_10.x | sudo bash - \
  && apt-get install -y nodejs

RUN PREFIX=/usr/share make install
RUN useradd -ms /bin/bash hue && chown -R hue /usr/share/hue

# Build the docs (not in Makefile yet)
# RUN hugo --source docs/docs-site

# Only keep install dir
WORKDIR /usr/share/hue
RUN rm -rf /hue

# Install DB connectors
RUN ./build/env/bin/pip install psycopg2-binary

COPY tools/docker/hue/conf desktop/conf
COPY tools/docker/hue/startup.sh .

EXPOSE 8888
CMD ["./startup.sh"]
