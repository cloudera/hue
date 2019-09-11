FROM centos:7

LABEL description="Hue Project https://github.com/cloudera/hue"

ARG GBN
ARG GSHA
ARG GBRANCH
ARG VERSION
ARG HUEUSER

# Set the environment variable
ENV NAME="hue" \
    HUE_HOME="/opt/${HUEUSER}" \
    HUE_CONF="/etc/hue" \
    HUE_BUILDNO=${GBN} \
    HUE_SHAURL=${GSHA} \
    HUE_BRANCHURL=${GBRANCH} \
    HUE_VERSION=${VERSION} \
    HUE_BIN="/opt/${HUEUSER}/build/env/bin" \
    PATH=$PATH:$HUE_BIN \
    SUPERVISOR_VERSION=4.0.2 \
    HUE_USER=${HUEUSER}

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
RUN groupadd -g 1123 ${HUE_USER} && useradd -g 1123 -d ${HUE_HOME} -s /bin/bash -u 1123 ${HUE_USER}
WORKDIR /opt/${HUE_USER}
COPY hue ${HUE_HOME}
COPY hue.sh ${HUE_HOME}/hue.sh
RUN $HUE_BIN/pip install psycopg2-binary
RUN chown -R ${HUE_USER}:${HUE_USER} ${HUE_HOME} && \
    mkdir -p /var/log/${HUE_USER} && \
    chown -R ${HUE_USER}:${HUE_USER} /var/log/${HUE_USER} && \
    mkdir -p ${HUE_CONF} && \
    chown -R ${HUE_USER}:${HUE_USER} ${HUE_CONF} && \
    echo "${HUE_USER} ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/${HUE_USER} && \
    chmod 0440 /etc/sudoers.d/${HUE_USER}

ENV HUE_CONF_DIR ${HUE_CONF}/conf
COPY hueconf ${HUE_CONF}/conf

RUN ln -s ${HUE_CONF}/conf/log.conf ${HUE_HOME}/desktop/conf/log.conf; \
    ln -s ${HUE_CONF}/conf/log4j.properties ${HUE_HOME}/desktop/conf/log4j.properties

# supervisor stuff
ADD supervisor-files/etc/supervisord.conf /etc/supervisord.conf
RUN mkdir -p /etc/supervisor.d/ && chmod +w /etc/supervisor.d
ADD supervisor-files/hue_server.conf /etc/supervisor.d/
ADD supervisor-files/hue_ktrenewer.conf /etc/supervisor.d/

EXPOSE 8888 9111

USER ${HUE_USER}
CMD ["/usr/bin/supervisord","-c","/etc/supervisord.conf"]
