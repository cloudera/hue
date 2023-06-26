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
        python38 \
        python38-devel \
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

RUN set -eux; \
      /usr/bin/pip3.8 install supervisor \
      && curl -s https://files.pythonhosted.org/packages/45/78/4621eb7085162bc4d2252ad92af1cc5ccacbd417a50e2ee74426331aad18/psycopg2_binary-2.9.3-cp38-cp38-musllinux_1_1_x86_64.whl -o /tmp/psycopg2_binary-2.9.3-cp38-cp38-musllinux_1_1_x86_64.whl \
      && dnf install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm \
      && yum install -y postgresql11 \
      && curl -sL https://rpm.nodesource.com/setup_14.x | bash - \
        && yum install -y nodejs \
        && yum clean all -y  \
        && rm -rf /var/cache/yum

# kubernetes pod health check
COPY healthz.sh /
RUN chmod +x /healthz.sh

CMD ["/bin/bash"]
