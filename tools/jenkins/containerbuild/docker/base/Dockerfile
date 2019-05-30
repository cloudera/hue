FROM ubuntu:18.04

LABEL description="Hue Project https://github.com/cloudera/hue"

RUN apt-get update -y && apt-get install -y \
  apache2 \
  build-essential \
  libkrb5-dev \
  libmysqlclient-dev \
  libssl-dev \
  libsasl2-dev \
  libsasl2-modules-gssapi-mit \
  libsqlite3-dev \
  libtidy-dev \
  libxml2-dev \
  libxslt-dev \
  libffi-dev \
  libldap2-dev \
  libpq-dev \
  python-dev \
  python-setuptools \
  libgmp3-dev \
  libz-dev \
  software-properties-common \
  curl \
  git \
  rsync \
  sudo \
  maven \
  gcc \
  swig \
  openssl \
  xmlsec1 \
  libxmlsec1-openssl \
  hugo \
   && rm -rf /var/lib/apt/lists/*

RUN apt-get update -y

# Need recent version for Ubuntu
RUN curl -sL https://deb.nodesource.com/setup_10.x | sudo bash - \
  && apt-get install -y nodejs

RUN mkdir -p /home/hue
RUN groupadd -g 1123 hue
RUN useradd -g 1123 -l -M -s /bin/bash -u 1123 hue && chown -R hue /home/hue

WORKDIR /home/hue
ENV PREFIX=/opt

CMD ["/bin/bash"]
