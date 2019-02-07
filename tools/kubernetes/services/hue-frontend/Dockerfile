FROM ubuntu:16.04

RUN apt-get update -y && apt-get install -y \
  build-essential \
  libkrb5-dev \
  libmysqlclient-dev \
  libssl-dev \
  libsasl2-dev \
  libsasl2-modules-gssapi-mit \
  libsqlite3-dev \
  libtidy-0.99-0 \
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
  git \
  sudo \
  maven \
   && rm -rf /var/lib/apt/lists/*

RUN add-apt-repository -y ppa:webupd8team/java
RUN apt-get update -y
RUN echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | sudo /usr/bin/debconf-set-selections
RUN apt-get install -y oracle-java8-installer

ADD hue /hue
RUN cd /hue && PREFIX=/usr/share make install
COPY conf /usr/share/hue/desktop/conf
EXPOSE 8888
RUN useradd -ms /bin/bash hue && chown -R hue /usr/share/hue
WORKDIR  /usr/share/hue
RUN ./build/env/bin/pip install psycopg2-binary
# dev tools
COPY ./startup.sh /usr/share/hue
CMD ["./startup.sh"]