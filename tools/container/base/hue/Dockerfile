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

# Install libtool without conflicts
RUN apk --no-cache --force-overwrite add libtool

# Set JAVA_HOME environment variable
ENV JAVA_HOME="/usr/lib/jvm/java-1.8-openjdk"
ENV PATH="$JAVA_HOME/bin:$PATH"

# Install openssl 3.4.0
RUN set -eux; \
    mkdir -p /tmp/ssl_download && cd /tmp/ssl_download && \
    curl -O -L https://github.com/openssl/openssl/releases/download/openssl-3.4.0/openssl-3.4.0.tar.gz && \
    tar -xzf openssl-3.4.0.tar.gz && \
    cd openssl-3.4.0 && \
    perl ./Configure \
         linux-$(uname -m) \
         --prefix=/usr \
         --libdir=lib \
         --openssldir=/etc/ssl \
         enable-ktls \
         enable-jitter \
         shared \
         enable-pie \
         no-zlib \
         no-async \
         no-comp \
         no-idea \
         no-mdc2 \
         no-rc5 \
         no-ec2m \
         no-sm2 \
         no-sm4 \
         no-ssl3 \
         no-seed \
         no-docs \
         no-weak-ssl-ciphers \
         -Wa,--noexecstack && \
      perl configdata.pm --dump && \
      make -j$(nproc) && \
      make install && \
      rm -f /etc/ssl/openssl.cnf /etc/ssl/openssl.cnf.dist /etc/ssl/ct_log_list.cnf /etc/ssl/ct_log_list.cnf.dist

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

# Setup openssl.cnf
RUN mkdir -p /etc/ssl
COPY openssl.cnf /etc/ssl
RUN chmod 755 /etc/ssl/openssl.cnf

CMD ["/bin/bash"]
