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
    PATH=$PATH:$HUE_BIN \
    SUPERVISOR_VERSION=4.0.2

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
      nmap-ncat \
      ncurses-devel \
      openldap-devel \
      openssl-devel \
      python-devel \
      python-setuptools \
      readline-devel \
      sqlite-devel \
      sudo \
      xmlsec1 \
      zlib-devel

RUN easy_install supervisor

RUN curl -sL https://rpm.nodesource.com/setup_10.x | bash - \
      && yum install -y nodejs \
      && yum clean all -y

# kubernetes health check
COPY healthz.sh /

# create hue user
RUN groupadd -g 1123 hue && useradd -g 1123 -d ${HUE_HOME} -s /bin/bash -u 1123 hue
WORKDIR /opt/hue
COPY hue ${HUE_HOME}
RUN $HUE_BIN/pip install psycopg2-binary
RUN chown -R hue:hue ${HUE_HOME} && \
    mkdir -p /var/log/hue && \
    chown -R hue:hue /var/log/hue && \
    mkdir -p ${HUE_CONF} && \
    chown -R hue:hue ${HUE_CONF} && \
    echo "hue ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/hue && \
    chmod 0440 /etc/sudoers.d/hue

ENV HUE_CONF_DIR ${HUE_CONF}/conf
COPY hueconf ${HUE_CONF}/conf

RUN ln -s ${HUE_CONF}/conf/log.conf ${HUE_HOME}/desktop/conf/log.conf; \
    ln -s ${HUE_CONF}/conf/log4j.properties ${HUE_HOME}/desktop/conf/log4j.properties

COPY hue.sh ${HUE_HOME}/hue.sh

# supervisor stuff
ADD supervisor-files/etc/supervisord.conf /etc/supervisord.conf
RUN mkdir -p /etc/supervisor.d/ && chmod +w /etc/supervisor.d
ADD supervisor-files/hue_server.conf /etc/supervisor.d/
ADD supervisor-files/hue_ktrenewer.conf /etc/supervisor.d/

EXPOSE 8888 9111

USER hue
CMD ["/usr/bin/supervisord","-c","/etc/supervisord.conf"]
