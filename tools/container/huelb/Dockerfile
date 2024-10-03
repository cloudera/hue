FROM ${HUELBBASE_VERSION}

LABEL description="Hue Project https://github.com/cloudera/hue"

ARG GBN
ARG GSHA
ARG GBRANCH
ARG VERSION
ARG HUEUSER

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

USER root

# Switch to non-root default user
RUN groupadd -g 1000 ${HUEUSER} && \
    useradd -g 1000 -d ${HUE_HOME} -s /bin/bash -u 1000 ${HUEUSER}

RUN mkdir -p ${HUE_LOG_DIR} && chown -R ${HUEUSER}:${HUEUSER} ${HUE_LOG_DIR}
RUN echo "Include /etc/hue_httpd.conf" >> /etc/httpd.conf

COPY --chown=${HUEUSER}:${HUEUSER} static ${HUE_HOME}/build/static
COPY --chown=${HUEUSER}:${HUEUSER} hue_httpd.conf /etc/hue_httpd.conf
COPY --chown=${HUEUSER}:${HUEUSER} hue.conf /etc/httpd/conf.d/hue.conf
COPY --chown=${HUEUSER}:${HUEUSER} run_httpd.sh ${HUE_HOME}
RUN sed -i "s|Listen 80|Listen 8080|g" /etc/httpd.conf && sed -i "s|User apache|User hive|g" /etc/httpd.conf && sed -i "s|Group apache|Group hive|g" /etc/httpd.conf
RUN chmod -v +x ${HUE_HOME}/run_httpd.sh
# log localtion /var/log/apache2/
RUN mkdir -p /run
RUN chown -R ${HUEUSER}:${HUEUSER} /run
RUN mkdir -p /tmp/httpd
RUN chown -R ${HUEUSER}:${HUEUSER} /tmp/httpd
RUN chown -R ${HUEUSER}:${HUEUSER} /var/log/apache2
RUN chown -R ${HUEUSER}:${HUEUSER} /var/run/apache2

COPY huelb-notice.txt ${HUE_HOME}/NOTICE.txt

EXPOSE 8080
# https://httpd.apache.org/docs/2.4/stopping.html#gracefulstop
STOPSIGNAL SIGINT

# Switch to non-root default user
USER hive
ENV USER hive
WORKDIR ${HUE_HOME}
CMD ["./run_httpd.sh"]
