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
    DESKTOP_LOG_DIR="/var/log/${HUEUSER}" \
    HUE_BUILDNO=${GBN} \
    HUE_SHAURL=${GSHA} \
    HUE_BRANCHURL=${GBRANCH} \
    HUE_VERSION=${VERSION} \
    HUE_BIN="/opt/${HUEUSER}/build/env/bin" \
    PATH=$PATH:${HUE_BIN} \
    SUPERVISOR_VERSION=4.0.2

USER root

# Switch to non-root default user
RUN groupadd -g 1000 ${HUEUSER} && \
    useradd -g 1000 -s /bin/bash -u 1000 ${HUEUSER}

COPY ${HUEUSER} ${HUE_HOME}
COPY hue.sh ${HUE_HOME}/hue.sh

# Install psycopg2-binary
RUN $HUE_BIN/python3.8 -m pip install --upgrade pip --force &&  $HUE_BIN/pip install psycopg2-binary

COPY hueconf ${HUE_CONF}/conf
COPY hueconf/log.conf ${HUE_HOME}/desktop/conf/log.conf
COPY hueconf/gunicorn_log.conf ${HUE_HOME}/desktop/conf/gunicorn_log.conf
COPY hueconf/log4j.properties ${HUE_HOME}/desktop/conf/log4j.properties
COPY hue-notice.txt ${HUE_HOME}/NOTICE.txt

# supervisor stuff
COPY supervisor-files/etc/supervisord.conf /etc/supervisord.conf
COPY supervisor-files/hue_server.conf /etc/supervisor.d/
COPY supervisor-files/hue_ktrenewer.conf /etc/supervisor.d/
COPY supervisor-files/hue_loglistener.conf /etc/supervisor.d/
COPY supervisor-files/hue_celery.conf /etc/supervisor.d/
COPY supervisor-files/hue_redis.conf /etc/supervisor.d/

# Remove chardet package
RUN rm -rf ${HUE_HOME}/build/env/lib/python3.8/site-packages/pip/_vendor/chardet

EXPOSE 8888 9111 6379

# Switch to non-root default user
USER hive
ENV USER hive
WORKDIR ${HUE_HOME}
CMD ["/usr/bin/supervisord","-c","/etc/supervisord.conf"]
