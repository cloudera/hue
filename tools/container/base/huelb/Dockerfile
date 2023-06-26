FROM registry.access.redhat.com/ubi8/ubi as base-ubi-8

LABEL description="Hue Project https://github.com/cloudera/hue"

# Set the environment variable
ENV NAME="basehue"

RUN set -eux; \
      yum install -y \
        hostname \
        httpd \
        httpd-tools \
        gettext \
        nmap-ncat && \
      yum clean all -y && \
      rm -rf /var/cache/yum

# kubernetes pod health check
COPY healthz.sh /
RUN chmod +x /healthz.sh

EXPOSE 80

CMD ["/usr/sbin/apachectl"]
