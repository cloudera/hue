FROM docker-private.infra.cloudera.com/cloudera_base/hardened/cloudera-base:v1.0.0-minimal AS cldr-v1mini

LABEL description="Hue Project https://github.com/cloudera/hue"

# Set the environment variable
ENV NAME="basehue"

USER root

RUN apk --no-cache add \
    apache2 \
    apache2-utils \
    gettext \
    nmap netcat-openbsd iftop procps net-tools bind-tools systemd

# kubernetes pod health check
COPY healthz.sh /
RUN chmod +x /healthz.sh

EXPOSE 80

CMD ["/bin/bash"]
