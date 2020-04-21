FROM registry.access.redhat.com/ubi7/ubi as base-ubi-7

LABEL description="Hue Project https://github.com/cloudera/hue"

# Set the environment variable
ENV NAME="basehue"

# Required for building Hue
RUN set -eux; \
    yum install -y \
      ant \
      asciidoc \
      bzip2-devel \
      curl \
      cyrus-sasl-devel \
      cyrus-sasl-gssapi \
      cyrus-sasl-plain \
      gcc \
      gcc-c++ \
      gettext \
      git \
      gmp-devel \
      java-1.8.0-openjdk-devel \
      krb5-devel \
      krb5-libs \
      krb5-workstation \
      libffi-devel \
      libtidy \
      libxml2-devel \
      libxslt-devel \
      make \
      maven \
      mysql-devel \
      nc \
      ncurses-devel \
      nmap-ncat \
      openldap-devel \
      openssl \
      openssl-devel \
      postgresql \
      postgresql-libs \
      python-devel \
      python-setuptools \
      readline-devel \
      sqlite-devel \
      sudo \
      swig \
      tar \
      which \
      xmlsec1 \
      xmlsec1-openssl \
      zlib-devel

RUN set -eux; easy_install supervisor pip

RUN curl -s https://files.pythonhosted.org/packages/a1/92/a27986cb7b4bddc7d57781a0e1163d683110907edfca1db3fbce25536492/psycopg2_binary-2.8.3-cp27-cp27mu-manylinux1_x86_64.whl -o /tmp/psycopg2_binary-2.8.3-cp27-cp27mu-manylinux1_x86_64.whl

RUN set -eux ; \
      curl -sL https://rpm.nodesource.com/setup_10.x | bash - \
        && yum install -y nodejs \
        && yum clean all -y

CMD ["/bin/bash"]
