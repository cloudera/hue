FROM registry.access.redhat.com/ubi7/ubi as base-ubi-7

LABEL description="Hue Project https://github.com/cloudera/hue"

# Set the environment variable
ENV NAME="basehue"

RUN set -eux; \
      yum install -y \
        hostname \
        httpd \
        httpd-tools \
        gettext \
        nmap-ncat

# kubernetes pod health check
COPY healthz.sh /
RUN chmod +x /healthz.sh

EXPOSE 80

CMD ["/usr/sbin/apachectl"]
