FROM httpd:2.4

LABEL description="Hue Project https://github.com/cloudera/hue"

# Set the environment variable
ENV NAME="hue" \
    HUE_VERSION="4.0.0" \
    HUE_BUILDNO="1" \
    HUE_HOME="/opt/hue" \
    HUE_CONF="/etc/hue" \
    HUE_BIN="/opt/hue/build/env/bin" \
    PATH=$PATH:$HUE_BIN

RUN echo "Include /usr/local/apache2/conf/hue_httpd.conf" >> /usr/local/apache2/conf/httpd.conf

RUN groupadd -g 1123 hue && useradd -g 1123 -d ${HUE_HOME} -s /bin/bash -u 1123 hue

COPY static ${HUE_HOME}/build/static

WORKDIR ${HUE_HOME}

COPY hue_httpd.conf /usr/local/apache2/conf/hue_httpd.conf

EXPOSE 80
