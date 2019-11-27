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

# create hue user
RUN groupadd -g 1123 ${HUEUSER} && useradd -g 1123 -d ${HUE_HOME} -s /bin/bash -u 1123 ${HUEUSER}

RUN mkdir -p ${HUE_LOG_DIR} && chown -R ${HUEUSER}:${HUEUSER} ${HUE_LOG_DIR}
RUN echo "Include /etc/httpd/conf.d/hue_httpd.conf" >> /etc/httpd/conf/httpd.conf

COPY static ${HUE_HOME}/build/static
COPY hue_httpd.conf /etc/httpd/conf.d/hue_httpd.conf
COPY hue.conf /etc/httpd/conf.d/hue.conf
COPY run_httpd.sh ${HUE_HOME}
RUN chown -R ${HUEUSER}:${HUEUSER} ${HUE_HOME}/build/static \
      /etc/httpd/conf.d/hue* \
      ${HUE_HOME}/run_httpd.sh && chmod -v +x ${HUE_HOME}/run_httpd.sh

EXPOSE 80
# https://httpd.apache.org/docs/2.4/stopping.html#gracefulstop
STOPSIGNAL SIGINT

WORKDIR ${HUE_HOME}
CMD ["run_httpd.sh"]
