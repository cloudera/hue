FROM registry.access.redhat.com/ubi8/ubi as base-ubi-8

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

RUN set -eux && \
      yum install -y \
        hostname \
        java-1.8.0-openjdk \
        gettext \
        nmap-ncat \
        sudo && \
      yum clean all && \
      rm -rf /var/cache/yum

# create hue user
RUN groupadd -g 1000 ${HUEUSER} && useradd -g 1000 -d ${HUE_QP_HOME} -s /bin/bash -u 1000 ${HUEUSER}

COPY --chown=${HUEUSER}:${HUEUSER} target ${HUE_QP_HOME}
COPY --chown=${HUEUSER}:${HUEUSER} target/conf ${HUE_QP_CONF_DIR}

# kubernetes pod health check
COPY healthz.sh /
RUN chmod +x /healthz.sh

# Setup directory structure
# sudo privilege
RUN mkdir -p ${HUE_QP_LOG_DIR} && chown -R ${HUEUSER}:${HUEUSER} ${HUE_QP_LOG_DIR} && \
    mkdir -p ${HUE_QP_PID_DIR} && chown -R ${HUEUSER}:${HUEUSER} ${HUE_QP_PID_DIR} && \
    mkdir -p ${HUE_CONF} && chown -R ${HUEUSER}:${HUEUSER} ${HUE_CONF} && \
    echo "${HUEUSER} ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/${HUEUSER} && \
    chmod 0440 /etc/sudoers.d/${HUEUSER} && \
    chmod +x /healthz.sh

EXPOSE 8080 9090 9091
WORKDIR ${HUE_QP_HOME}

USER ${HUEUSER}
ENTRYPOINT ["/opt/hive/bin/hue-query-processor", "start"]
