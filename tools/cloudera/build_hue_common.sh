#!/usr/bin/env bash

function big_console_header() {
  set +x
  local text="$*"
  local spacing=$(( (75+${#text}) /2 ))
  printf "\n\n"
  echo "============================================================================"
  echo "============================================================================"
  printf "%*s\n"  ${spacing} "${text}"
  echo "============================================================================"
  echo "============================================================================"
  printf "\n\n"
  set -x
}

function check_python_path() {
  export python38_bin="$PYTHON38_PATH/bin/python3.8"
  if [ ! -e "$python38_bin" ]; then
    echo "Python bin does not exists at " $python38_bin
    exit 1
  fi
  export pip38_bin="$PYTHON38_PATH/bin/pip3.8"
}

function check_sqlite3() {
  export sqlit3_bin="$SQLITE3_PATH"
  if [ ! -e "$sqlit3_bin" ]; then
    echo "sqlit3 bin does not exists at " $sqlit3_bin
    exit 1
  fi
}

function sles12_install() {
  if [[ $FORCEINSTALL -eq 1 ]]; then
    # pre-req install
    sudo -- sh -c 'zypper install -y cyrus-sasl-gssapi \
      cyrus-sasl-plain \
      java-11-openjdk \
      java-11-openjdk-devel \
      java-11-openjdk-headless \
      krb5-client pam_krb5 krb5-appl-clients krb5-plugin-kdb-ldap \
      libpcap \
      ncurses-devel \
      nmap \
      xmlsec1 xmlsec1-devel  xmlsec1-openssl-devel'
    # MySQLdb install
    sudo -- sh -c 'zypper install -y libmysqlclient-devel libmysqlclient18 libmysqld18 libmysqld-devel'
    # NODEJS 14 install
    sudo -- sh -c 'zypper install -y npm14 nodejs14'
    # Pip modules install
    sudo pip38_bin=${pip38_bin} -- sh -c '${pip38_bin} install virtualenv virtualenv-make-relocatable mysqlclient'
    # sqlite3 install
    sudo -- sh -c 'curl --insecure -o sqlite-autoconf-3350500.tar.gz https://www.sqlite.org/2021/sqlite-autoconf-3350500.tar.gz && \
        tar zxvf sqlite-autoconf-3350500.tar.gz && \
        cd sqlite-autoconf-3350500 && \
        ./configure --prefix=/usr/local/ && make && make install'
    export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
  fi
}

function centos7_install() {
  if [[ $FORCEINSTALL -eq 1 ]]; then
    # pre-req install
    sudo -- sh -c 'yum install -y cyrus-sasl-gssapi \
      cyrus-sasl-plain \
      java-11-openjdk \
      java-11-openjdk-devel \
      java-11-openjdk-headless \
      krb5-workstation \
      libpcap \
      ncurses-devel \
      nmap-ncat \
      xmlsec1 \
      xmlsec1-openssl \
      unzip'
    # MySQLdb install
    sudo -- sh -c 'curl -sSLO https://dev.mysql.com/get/mysql80-community-release-el7-5.noarch.rpm && \
        rpm -ivh mysql80-community-release-el7-5.noarch.rpm && \
        yum install -y mysql-community-libs mysql-community-client-plugins mysql-community-common'
    # NODEJS 14 install
    sudo -- sh -c 'yum install -y rh-nodejs14-nodejs'
    # sqlite3 install
    sudo -- sh -c 'curl -o sqlite-autoconf-3350500.tar.gz https://www.sqlite.org/2021/sqlite-autoconf-3350500.tar.gz && \
        tar zxvf sqlite-autoconf-3350500.tar.gz && \
        cd sqlite-autoconf-3350500 && \
        ./configure --prefix=/usr/local/ && make && make install'
    # python3.8 re install for sqlite3 3.35.5 or higher version
    sudo LD_LIBRARY_PATH=/usr/local/lib:$ORACLE_INSTANTCLIENT19_PATH:$LD_LIBRARY_PATH \
         LD_RUN_PATH=/usr/local/lib:$ORACLE_INSTANTCLIENT19_PATH:$LD_RUN_PATH \
         -- sh -c 'curl -o Python-3.8.13.tgz https://www.python.org/ftp/python/3.8.13/Python-3.8.13.tgz && \
      tar zxvf Python-3.8.13.tgz && \
      cd Python-3.8.13 && \
      ./configure --enable-shared --prefix=/opt/cloudera/cm-agent && \
      make install'
    # Pip modules install
    sudo pip38_bin=${pip38_bin} -- sh -c '${pip38_bin} install virtualenv virtualenv-make-relocatable mysqlclient'
  fi
}

function redhat8_install() {
  if [[ $FORCEINSTALL -eq 1 ]]; then
    # pre-req install
    sudo -- sh -c 'yum install -y \
      java-11-openjdk \
      java-11-openjdk-devel \
      java-11-openjdk-headless \
      krb5-workstation \
      ncurses-devel \
      nmap-ncat \
      xmlsec1 \
      xmlsec1-openssl \
      libss \
      ncurses-c++-libs'
    # MySQLdb install
    sudo -- sh -c 'yum install -y python3-mysqlclient'
    # NODEJS 14 install
    sudo -- sh -c 'curl -sL https://rpm.nodesource.com/setup_14.x | bash - && yum install -y nodejs'
    # Pip modules install
    sudo pip38_bin=${pip38_bin} -- sh -c '${pip38_bin} install virtualenv virtualenv-make-relocatable mysqlclient'
    # sqlite3 install
    sudo -- sh -c 'curl -o sqlite-autoconf-3350500.tar.gz https://www.sqlite.org/2021/sqlite-autoconf-3350500.tar.gz && \
      tar zxvf sqlite-autoconf-3350500.tar.gz && \
      cd sqlite-autoconf-3350500 && \
      ./configure --prefix=/usr/local/ && make && make install'
    export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
  fi
}

function ubuntu18_install() {
    if [[ $FORCEINSTALL -eq 1 ]]; then
    # pre-req install
    sudo -- sh -c 'DEBIAN_FRONTEND=noninteractive apt -qq -y install  \
        krb5-user \
        krb5-kdc \
        krb5-config \
        libkrb5-dev'
    sudo -- sh -c 'apt -y install \
        ldap-utils \
        libpython3.8-dev \
        libpython3.8-minimal \
        libpython3.8-stdlib \
        libxmlsec1 \
        libxmlsec1-openssl \
        netcat \
        nmap \
        python3-asn1crypto \
        python3-cffi-backend \
        python3-crypto \
        python3-cryptography \
        python3-keyring \
        python3-psycopg2 \
        python3-setuptools \
        python3-wheel \
        python3.8-venv \
        zlibc'
    # MySQLdb install
    # It is pre-installed
    # NODEJS 14 install
    sudo -- sh -c 'curl -sL https://deb.nodesource.com/setup_14.x | sudo bash - && \
      apt -y install nodejs'
    # Pip modules install
    sudo pip38_bin=${pip38_bin} -- sh -c '${pip38_bin} install virtualenv virtualenv-make-relocatable mysqlclient'
    # sqlite3 install
    sudo -- sh -c 'curl -o sqlite-autoconf-3350500.tar.gz https://www.sqlite.org/2021/sqlite-autoconf-3350500.tar.gz && \
        tar zxvf sqlite-autoconf-3350500.tar.gz && \
        cd sqlite-autoconf-3350500 && \
        ./configure --prefix=/usr/local/ && make && make install'
    export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
  fi
}

function ubuntu20_install() {
    if [[ $FORCEINSTALL -eq 1 ]]; then
    # pre-req install
    sudo -- sh -c 'DEBIAN_FRONTEND=noninteractive apt -qq -y install  \
        krb5-user \
        krb5-kdc \
        krb5-config \
        libkrb5-dev'
    sudo -- sh -c 'apt -y install \
        ldap-utils \
        libpython3.8-dev \
        libpython3.8-minimal \
        libpython3.8-stdlib \
        libxmlsec1 \
        libxmlsec1-openssl \
        netcat \
        nmap \
        python-asn1crypto \
        python3-crypto \
        python3-cryptography \
        python3-keyring \
        python3-psycopg2 \
        python3-setuptools \
        python3-wheel \
        python3.8-venv \
        zlibc \
        openssl \
        sudo \
        tar \
        util-linux'
    # MySQLdb install
    # It is pre-installed
    # NODEJS 14 install
    sudo -- sh -c 'curl -sL https://deb.nodesource.com/setup_14.x | sudo bash - && \
      apt -y install nodejs'
    # Pip modules install
    sudo pip38_bin=${pip38_bin} -- sh -c '${pip38_bin} install virtualenv virtualenv-make-relocatable mysqlclient'
    # sqlite3 install
    sudo -- sh -c 'curl -o sqlite-autoconf-3350500.tar.gz https://www.sqlite.org/2021/sqlite-autoconf-3350500.tar.gz && \
        tar zxvf sqlite-autoconf-3350500.tar.gz && \
        cd sqlite-autoconf-3350500 && \
        ./configure --prefix=/usr/local/ && make && make install'
    export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
  fi
}
