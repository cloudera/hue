FROM docker-sandbox.infra.cloudera.com/chainguard/cloudera-python-jdk:py39-jdk8 AS py39-jdk8

LABEL description="Hue Project https://github.com/cloudera/hue"

ARG GBN
ARG GSHA
ARG GBRANCH
ARG VERSION
ARG HUEUSER
ARG HUE_CONF

# Set the environment variable
ENV NAME="hue" \
    HUE_USER=${HUEUSER} \
    HUE_QP_HOME="/opt/${HUEUSER}" \
    HUE_QP_CONF_DIR="${HUE_CONF}/conf" \
    HUE_QP_LOG_DIR="/var/log/${HUEUSER}" \
    HUE_QP_PID_DIR="/var/run/${HUEUSER}" \
    HUE_BUILDNO=${GBN} \
    HUE_SHAURL=${GSHA} \
    HUE_BRANCHURL=${GBRANCH} \
    HUE_VERSION=${VERSION} \
    HUE_BIN="/opt/${HUEUSER}/build/env/bin" \
    PATH=$PATH:${HUE_BIN} \
    SUPERVISOR_VERSION=4.0.2

USER root
RUN apk --no-cache add \
    gettext \
    nmap \
    maven \
    sudo \
    nmap netcat-openbsd iftop procps net-tools bind-tools \
    && rm -rf /var/cache/apk/*

# create hue user
RUN groupadd -g 1000 ${HUEUSER} && useradd -g 1000 -s /bin/bash -u 1000 ${HUEUSER}

COPY target ${HUE_QP_HOME}
COPY target/conf ${HUE_QP_CONF_DIR}
COPY hueqp-notice.txt ${HUE_QP_HOME}/NOTICE.txt
# kubernetes pod health check
COPY healthz.sh /

EXPOSE 8080 9090 9091 30700
WORKDIR ${HUE_QP_HOME}

USER ${HUEUSER}
ENTRYPOINT ["/opt/hive/bin/hue-query-processor", "start"]
