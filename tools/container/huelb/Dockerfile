FROM httpd:2.4

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

RUN apt-get update; \
    apt-get install -y --no-install-recommends \
      netcat \
      ; \
    rm -r /var/lib/apt/lists/*;

RUN echo "Include /usr/local/apache2/conf/hue_httpd.conf" >> /usr/local/apache2/conf/httpd.conf

RUN groupadd -g 1123 hue && useradd -g 1123 -d ${HUE_HOME} -s /bin/bash -u 1123 hue

COPY static ${HUE_HOME}/build/static

COPY run_httpd.sh ${HUE_HOME}
COPY healthz.sh /

WORKDIR ${HUE_HOME}

COPY hue_httpd.conf /usr/local/apache2/conf/hue_httpd.conf

EXPOSE 80

CMD ["run_httpd.sh"]
