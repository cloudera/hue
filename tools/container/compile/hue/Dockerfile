FROM docker-private.infra.cloudera.com/cloudera_base/hardened/cloudera-python:3.9 AS cldr-py39

LABEL description="Hue Project https://github.com/cloudera/hue"

# Set the environment variable
ENV NAME="basehue"
ENV PYTHON_VER=python3.9

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
    libtool \
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
    openssl=3.4.0-r3 \
    openssl-dev=3.4.0-r4 \
    rsync \
    sqlite-dev \
    sudo \
    zlib-dev \
    busybox \
    ca-certificates-bundle \
    jitterentropy-library-dev=3.5.0-r0 \
    jitterentropy-library=3.5.0-r0 \
    openssf-compiler-options \
    perl \
    nmap netcat-openbsd iftop procps net-tools bind-tools shadow

# remove FIPS settings
RUN apk del openssl-config-fipshardened
RUN apk add openssl openssl-config
RUN apk cache clean

# Setup openssl.cnf
RUN mkdir -p /etc/ssl
COPY openssl.cnf /etc/ssl
RUN chmod 755 /etc/ssl/openssl.cnf

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

# Install redis
RUN set -eux; \
    curl -O http://download.redis.io/redis-stable.tar.gz && \
    tar xzf redis-stable.tar.gz && \
    cd redis-stable && \
    make && \
    make install && \
    cd .. && \
    rm -rf redis-stable redis-stable.tar.gz

CMD ["/bin/bash"]
