FROM docker-sandbox.infra.cloudera.com/chainguard/cloudera-python-jdk:py39-jdk8 AS py39-jdk8

LABEL description="Hue Project https://github.com/cloudera/hue"

# Set the environment variable
ENV NAME="basehue"

USER root
RUN apk add --no-cache gettext nmap maven
RUN rm -rf /var/cache/apk/*

RUN mkdir /root/.m2
ADD settings.xml /root/.m2/

CMD ["/bin/bash"]
