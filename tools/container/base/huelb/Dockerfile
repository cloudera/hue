FROM docker-private.infra.cloudera.com/cloudera_base/centos:7.6.1810 as base-centos-jdk

LABEL description="Hue Project https://github.com/cloudera/hue"

# Set the environment variable
ENV NAME="basehue"

RUN set -eux; \
      yum install -y \
        httpd \
        httpd-tools \
        gettext \
        nmap-ncat

# kubernetes pod health check
COPY healthz.sh /
RUN chmod +x /healthz.sh

EXPOSE 80

CMD ["/usr/sbin/apachectl"]
