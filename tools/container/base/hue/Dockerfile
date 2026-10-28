FROM registry.access.redhat.com/ubi8/ubi as base-ubi-8

LABEL description="Hue Project https://github.com/cloudera/hue"

# Set the environment variable
ENV NAME="basehue"

# Required libraries for running Hue
RUN set -eux; \
      yum install -y \
        bzip2-devel \
        curl \
        cyrus-sasl \
        cyrus-sasl-devel \
        cyrus-sasl-gssapi \
        cyrus-sasl-plain \
        gettext \
        gmp \
        java-1.8.0-openjdk-devel \
        krb5-devel \
        krb5-libs \
        krb5-workstation \
        libffi-devel \
        libxml2-devel \
        libxslt-devel \
        ncurses-devel \
        nmap-ncat \
        procps-ng \
        python3.11 \
        python3.11-devel \
        rsync \
        openldap-devel \
        openssl \
        openssl-devel \
        sqlite-devel \
        sudo \
        which \
        xmlsec1 \
        xmlsec1-openssl \
        zlib-devel

# Install redis
RUN set -eux; \
    dnf install -y gcc make && \
    curl -O http://download.redis.io/redis-stable.tar.gz && \
    tar xzf redis-stable.tar.gz && \
    cd redis-stable && \
    make && \
    make install && \
    cd .. && \
    rm -rf redis-stable redis-stable.tar.gz && \
    dnf clean all && \
    rm -rf /var/cache/yum

RUN set -eux; \
      # pip 26.2.2: older releases keep trusting the compromised eMudhra CAs through their vendored certifi.
      # Keep in sync with desktop/core/pip-bootstrap-requirements.txt.
      python3.11 -m pip install --upgrade pip==26.2.2 \
      && python3.11 -m pip install supervisor psycopg2-binary \
      && dnf install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm \
      && yum install -y postgresql15 \
      && curl -sL https://rpm.nodesource.com/setup_14.x | bash - \
        && yum install -y nodejs \
        && yum clean all -y  \
        && rm -rf /var/cache/yum

# kubernetes pod health check
COPY healthz.sh /
RUN chmod +x /healthz.sh

CMD ["/bin/bash"]
