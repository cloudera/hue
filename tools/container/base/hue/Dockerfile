FROM docker-private.infra.cloudera.com/cloudera_base/hardened/cloudera-python:3.8 AS cldr-py38

LABEL description="Hue Project https://github.com/cloudera/hue"

# Set the environment variable
ENV NAME="basehue"

USER root

RUN set -eux; \
    apk --no-cache add \
    autoconf \
    automake \
    build-base \
    bzip2-dev \
    curl \
    cyrus-sasl-dev \
    gettext \
    git \
    krb5 \
    krb5-dev \
    krb5-libs \
    libffi-dev \
    libxml2-dev \
    libxslt-dev \
    make \
    maven \
    ncurses-dev \
    nmap \
    nodejs \
    npm \
    openjdk-8 \
    openldap-dev \
    openssl \
    openssl-dev \
    rsync \
    sqlite-dev \
    sudo \
    zlib-dev \
    nmap netcat-openbsd iftop procps net-tools bind-tools shadow

# Install libtool without conflicts
RUN apk --no-cache --force-overwrite add libtool

# Set JAVA_HOME environment variable
ENV JAVA_HOME="/usr/lib/jvm/java-1.8-openjdk"
ENV PATH="$JAVA_HOME/bin:$PATH"

# Install xmlsec
RUN set -eux; \
    curl -O -L https://github.com/lsh123/xmlsec/releases/download/1.2.41/xmlsec1-1.2.41.tar.gz && \
    tar -xzf xmlsec1-1.2.41.tar.gz && \
    cd xmlsec1-1.2.41 && \
    ./configure --prefix=/usr && \
    make && \
    make install

RUN set -eux; \
    curl -O http://download.redis.io/redis-stable.tar.gz && \
    tar xzf redis-stable.tar.gz && \
    cd redis-stable && \
    make && \
    make install && \
    cd .. && \
    rm -rf redis-stable redis-stable.tar.gz

# Install required tools and dependencies
RUN pip3.8 install supervisor psycopg2-binary --no-cache-dir

# Install PostgreSQL client tools which include pg_dump and pg_restore
RUN apk --no-cache add postgresql-client
WORKDIR /workspace
EXPOSE 5432

# kubernetes pod health check
COPY healthz.sh /
RUN chmod +x /healthz.sh

# Setup openssl.cnf
RUN mkdir -p /etc/ssl
COPY openssl.cnf /etc/ssl
RUN chmod 755 /etc/ssl/openssl.cnf

CMD ["/bin/bash"]
