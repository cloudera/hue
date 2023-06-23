FROM registry.access.redhat.com/ubi8/ubi as base-ubi-8

LABEL description="Hue Project https://github.com/cloudera/hue"

# Set the environment variable
ENV NAME="basehue"
ENV PYTHON_VER=python3.8

# Required for building Hue
RUN set -eux; \
    yum install -y \
      bzip2-devel  \
      curl \
      cyrus-sasl \
      cyrus-sasl-devel \
      cyrus-sasl-gssapi \
      cyrus-sasl-plain \
      gcc \
      gcc-c++ \
      gettext \
      git \
      java-11-openjdk-devel \
      krb5-devel \
      krb5-libs \
      krb5-workstation \
      libffi-devel \
      libxml2-devel \
      libxslt-devel \
      make \
      maven \
      nc \
      ncurses-devel \
      nmap-ncat \
      openldap-devel \
      openssl \
      openssl-devel \
      python38 \
      python38-devel \
      rsync \
      sqlite-devel \
      sudo \
      tar \
      which \
      xmlsec1 \
      xmlsec1-openssl \
      zlib-devel

RUN set -eux; \
      curl -sL https://rpm.nodesource.com/setup_14.x | bash - \
        && yum install -y nodejs \
        && curl -sSLO https://repo.mysql.com/mysql80-community-release-el8-5.noarch.rpm \
        && rpm -ivh mysql80-community-release-el8-5.noarch.rpm \
        && yum install -y mysql-community-libs mysql-community-client-plugins mysql-community-common mysql-community-devel gcc \
        && yum clean all -y

CMD ["/bin/bash"]
