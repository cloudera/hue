FROM ubuntu1804:base

LABEL description="Hue Project https://github.com/cloudera/hue"

COPY hue /opt/hue
COPY docker/httpd/httpdstart /usr/local/bin/

EXPOSE 8889
CMD ["httpdstart"]
