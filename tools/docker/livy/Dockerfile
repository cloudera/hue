# Welcome to the official Livy (http://gethue.com) developer Dockerfile
FROM ubuntu:trusty
MAINTAINER The Hue Team "https://github.com/cloudera/hue"

RUN apt-get install -y software-properties-common
RUN add-apt-repository -y ppa:webupd8team/java
RUN apt-get update -y

RUN echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | sudo /usr/bin/debconf-set-selections
RUN apt-get install -y oracle-java8-installer

RUN apt-get install -q -y \
  git \
  maven \
  curl \
  m4 \
  ruby \
  texinfo \
  libbz2-dev \
  libcurl4-openssl-dev \
  libexpat-dev \
  libncurses-dev \
  zlib1g-dev

RUN useradd -ms /bin/bash ellie

USER ellie
WORKDIR /home/ellie
RUN yes |ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/linuxbrew/go/install)"
ENV PATH="/home/ellie/.linuxbrew/bin:$PATH"
ENV SPARK_HOME="/home/ellie/.linuxbrew/Cellar/apache-spark/1.5.1"
RUN brew update
RUN brew install apache-spark

RUN git clone https://github.com/cloudera/hue.git

WORKDIR hue/apps/spark/java

RUN mvn clean install -DskipTests

EXPOSE 8998
CMD ["./bin/livy-server"]
