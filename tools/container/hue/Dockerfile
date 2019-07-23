FROM centos:7

LABEL description="Hue Project https://github.com/cloudera/hue"

ARG GBN
ARG GSHA
ARG GBRANCH
ARG VERSION

# Set the environment variable
ENV NAME="hue" \
    HUE_HOME="/opt/hue" \
    HUE_CONF="/etc/hue" \
    HUE_BUILDNO=${GBN} \
    HUE_SHAURL=${GSHA} \
    HUE_BRANCHURL=${GBRANCH} \
    HUE_VERSION=${VERSION} \
    HUE_BIN="/opt/hue/build/env/bin" \
    PATH=$PATH:$HUE_BIN

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
RUN yum install -y \
      asciidoc \
      bzip2-devel \
      cyrus-sasl-devel \
      cyrus-sasl-gssapi \
      cyrus-sasl-plain \
      gmp-devel \
      krb5-devel \
      krb5-libs \
      krb5-workstation \
      libffi-devel \
      libtidy \
      libxml2-devel \
      libxslt-devel \
      ncurses-devel \
      openldap-devel \
      openssl-devel \
      python-devel \
      readline-devel \
      sqlite-devel \
      xmlsec1 \
      zlib-devel

RUN curl -sL https://rpm.nodesource.com/setup_10.x | bash - \
      && yum install -y nodejs \
      && yum clean all -y

RUN groupadd -g 1123 hue && useradd -g 1123 -d ${HUE_HOME} -s /bin/bash -u 1123 hue

COPY hue ${HUE_HOME}
RUN $HUE_BIN/pip install psycopg2-binary

RUN mkdir -p ${HUE_CONF}
ENV HUE_CONF_DIR ${HUE_CONF}/conf
COPY conf ${HUE_CONF}/conf
COPY startup.sh ${HUE_HOME}/startup.sh
EXPOSE 8888

WORKDIR /opt/hue
CMD ["/opt/hue/startup.sh"]
