FROM registry.access.redhat.com/ubi7/ubi as base-ubi-7

LABEL description="Hue Project https://github.com/cloudera/hue"

# Set the environment variable
ENV NAME="basehue"

# Required for building Hue
#RUN yum install -y \
#      ant \
#      curl \
#      gcc \
#      gcc-c++ \
#      git \
#      java-1.8.0-openjdk-devel \
#      maven \
#      make \
#      mysql-devel \
#      nc \
#      sudo \
#      tar \
#      vim-enhanced
#

# Required libraries for running Hue
RUN set -eux; \
      yum install -y \
        asciidoc \
        bzip2-devel \
        cyrus-sasl-devel \
        cyrus-sasl-gssapi \
        cyrus-sasl-plain \
        gettext \
        gmp-devel \
        java-1.8.0-openjdk-devel \
        krb5-devel \
        krb5-libs \
        krb5-workstation \
        libffi-devel \
        libtidy \
        libxml2-devel \
        libxslt-devel \
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

# kubernetes pod health check
COPY healthz.sh /
RUN chmod +x /healthz.sh

CMD ["/bin/bash"]
