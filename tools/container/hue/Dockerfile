FROM ${HUEBASE_VERSION}

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
    HUE_HOME="/opt/${HUEUSER}" \
    HUE_CONF_DIR="${HUE_CONF}/conf" \
    HUE_LOG_DIR="/var/log/${HUEUSER}" \
    HUE_BUILDNO=${GBN} \
    HUE_SHAURL=${GSHA} \
    HUE_BRANCHURL=${GBRANCH} \
    HUE_VERSION=${VERSION} \
    HUE_BIN="/opt/${HUEUSER}/build/env/bin" \
    PATH=$PATH:${HUE_BIN} \
    SUPERVISOR_VERSION=4.0.2

# Switch to non-root default user
RUN yum install -y microdnf && \
    microdnf install -y shadow-utils findutils && \
    groupadd -g 1000 ${HUEUSER} && \
    useradd -g 1000 -d ${HUE_HOME} -s /bin/bash -u 1000 ${HUEUSER}

COPY --chown=${HUEUSER}:${HUEUSER} ${HUEUSER} ${HUE_HOME}
COPY --chown=${HUEUSER}:${HUEUSER} hue.sh ${HUE_HOME}/hue.sh

# Install psycopg2-binary
RUN $HUE_BIN/python3.8 -m pip install --upgrade pip --force && $HUE_BIN/pip install psycopg2-binary

# Setup directory structure
RUN mkdir -p ${HUE_LOG_DIR} && chown -R ${HUEUSER}:${HUEUSER} ${HUE_LOG_DIR}
RUN mkdir -p ${HUE_CONF} && chown -R ${HUEUSER}:${HUEUSER} ${HUE_CONF}

# sudo privilege
RUN echo "${HUEUSER} ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/${HUEUSER} && \
    chmod 0440 /etc/sudoers.d/${HUEUSER}

COPY --chown=${HUEUSER}:${HUEUSER} hueconf ${HUE_CONF}/conf

RUN ln -s ${HUE_CONF}/conf/log.conf ${HUE_HOME}/desktop/conf/log.conf; \
    ln -s ${HUE_CONF}/conf/log4j.properties ${HUE_HOME}/desktop/conf/log4j.properties

# supervisor stuff
RUN mkdir -p /etc/supervisor.d/ && chmod +w /etc/supervisor.d && mkdir -p /var/log/root && chown -R ${HUEUSER}:${HUEUSER} /var/log/root
ADD supervisor-files/etc/supervisord.conf /etc/supervisord.conf
ADD supervisor-files/hue_server.conf /etc/supervisor.d/
ADD supervisor-files/hue_ktrenewer.conf /etc/supervisor.d/
RUN chown -R ${HUEUSER}:${HUEUSER} /etc/supervisord.conf && chown -R ${HUEUSER}:${HUEUSER} /etc/supervisor.d

# Remove chardet package
RUN rm -rf ${HUE_HOME}/build/env/lib/python3.8/site-packages/pip/_vendor/chardet

EXPOSE 8888 9111

# Switch to non-root default user
USER hive
ENV USER hive
WORKDIR ${HUE_HOME}
CMD ["/usr/local/bin/supervisord","-c","/etc/supervisord.conf"]
