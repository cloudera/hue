FROM ubuntu1804:base

LABEL description="Hue Project https://github.com/cloudera/hue"

COPY hue /opt/hue

RUN mkdir -p /etc/hue/conf
ENV HUE_CONF_DIR /etc/hue/conf
COPY docker/webapp/conf /etc/hue/conf

COPY docker/webapp/startup.sh /opt/hue

EXPOSE 8888
CMD ["/opt/hue/startup.sh"]
