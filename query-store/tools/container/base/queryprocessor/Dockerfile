FROM registry.access.redhat.com/ubi8/ubi as base-ubi-8

LABEL description="Hue Project https://github.com/cloudera/hue"

# Set the environment variable
ENV NAME="basehue"

RUN set -eux; \
      yum install -y \
        hostname \
        java-1.8.0-openjdk-devel \
        gettext \
        nmap-ncat

# Setting Maven Version that needs to be installed
ARG MAVEN_VERSION=3.6.3

RUN curl -fsSL https://archive.apache.org/dist/maven/maven-3/$MAVEN_VERSION/binaries/apache-maven-$MAVEN_VERSION-bin.tar.gz | tar xzf - -C /usr/share \
  && mv /usr/share/apache-maven-$MAVEN_VERSION /usr/share/maven \
  && ln -s /usr/share/maven/bin/mvn /usr/bin/mvn

RUN mkdir /root/.m2
ADD settings.xml /root/.m2/

CMD ["/bin/bash"]
