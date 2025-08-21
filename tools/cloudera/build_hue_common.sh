#!/usr/bin/env bash

big_console_header() {
  set +x
  local text="$*"
  local spacing=$(( (75+${#text}) /2 ))
  printf "\n\n============================================================================\n"
  printf "%*s\n"  ${spacing} "${text}"
  printf "============================================================================\n\n\n"
  set -x
}

is_supported_os() {
  local _arrayname=$1
  local _os=$2

  local _array=()
  eval "_array=(\"\${${_arrayname}[@]}\")"

  for item in "${_array[@]}"; do
    if [[ "$item" == "$_os" ]]; then
      return 0
    fi
  done
  return 1
}

is_supported_python_version() {
  local PYBIN="$1"
  local version="$2"
  IFS='.' read -r major minor patch <<< "$version"
  "$PYBIN" -c "import sys; exit(0) if sys.version_info >= ($major, $minor, $patch) else exit(1)"
  return $?
}

function install_build_dependencies() {
  local DOCKEROS=${1:-"ubuntu22"}
  echo "Installing build dependencies..."
  case "${DOCKEROS}" in
      ubuntu24|ubuntu22|ubuntu20|ubuntu18)
          sudo -- sh -c 'apt update && \
            apt install -y \
            build-essential \
            libbz2-dev libncurses5-dev libgdbm-dev libreadline-dev libkrb5-dev \
            liblzma-dev uuid-dev libldap2-dev libffi-dev zlib1g-dev libssl-dev wget curl'
          ;;
      redhat9|redhat8|redhat8-arm64|centos7)
          sudo -- sh -c 'yum groupinstall -y "Development Tools" && \
            yum install -y \
            bzip2-devel ncurses-devel gdbm-devel readline-devel krb5-devel \
            xz-devel libuuid-devel openldap-devel libffi-devel zlib-devel openssl-devel wget curl'
          ;;
      sles12|sles15)
          sudo -- sh -c 'zypper refresh'
          sudo -- sh -c 'zypper install -y \
            gcc gcc-c++ make \
            ncurses-devel gdbm-devel readline-devel krb5-devel \
            xz-devel libuuid-devel openldap2-devel libffi-devel zlib-devel libopenssl-devel wget curl'
          ;;
      *)
          echo "Unsupported OS: ${DOCKEROS}. Exiting."
          exit 1
          ;;
  esac
}

function install_sqlite3() {
  local install_prefix="$1"
  local version="3.35.5"
  sqlite_installed=0

  if [[ -e "${install_prefix}/bin/sqlite3" ]]; then
    local installed_version=$(${install_prefix}/bin/sqlite3 --version 2>&1 | awk '{print $1}')
    if [[ "$installed_version" == "$version" ]]; then
      if [[ -e "${install_prefix}/lib/libsqlite3.so" ]]; then
        echo "sqlite3 already installed"
        sqlite_installed=1
      fi
    fi
  fi

  if [[ $sqlite_installed -eq 0 ]]; then
    echo "Installing sqlite3..."
    # Fix curl library conflicts by prioritizing system libraries
    # Detect system library path based on architecture and OS
    local SYSTEM_LIB_PATH=""
    if [[ -d "/usr/lib/$(uname -m)-linux-gnu" ]]; then
      SYSTEM_LIB_PATH="/usr/lib/$(uname -m)-linux-gnu"
    elif [[ -d "/usr/lib64" ]]; then
      SYSTEM_LIB_PATH="/usr/lib64"
    else
      SYSTEM_LIB_PATH="/usr/lib"
    fi
    
    sudo LD_LIBRARY_PATH="${SYSTEM_LIB_PATH}:${LD_LIBRARY_PATH}" PATH=${PATH} install_prefix=${install_prefix} \
      -- sh -c 'cd /tmp && \
    mkdir -p ${install_prefix} && \
    curl -o sqlite-autoconf-3350500.tar.gz https://www.sqlite.org/2021/sqlite-autoconf-3350500.tar.gz && \
        tar zxvf sqlite-autoconf-3350500.tar.gz && \
        cd sqlite-autoconf-3350500 && \
        ./configure --prefix=${install_prefix} && make && make install && \
        libtool --finish ${install_prefix}/lib'
  fi
}

function install_python311() {
  local PYTHON_VERSION=${1:-"3.11.12"}
  local INSTALL_PREFIX=$2
  local LD_LIBRARY_PATH=$3
  local CPPFLAGS=$4
  local LDFLAGS=$5
  pushd . > /dev/null

  cd $HOME
  local PYTHON_TGZ="Python-${PYTHON_VERSION}.tgz"
  local PYTHON_SRC_DIR="Python-${PYTHON_VERSION}"

  export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/lib/mit/bin:$PATH

  echo "Installing Python ${PYTHON_VERSION}..."
  sudo PYTHON_VERSION=${PYTHON_VERSION} INSTALL_PREFIX=${INSTALL_PREFIX} \
    PYTHON_TGZ=${PYTHON_TGZ} PYTHON_SRC_DIR=${PYTHON_SRC_DIR} LD_LIBRARY_PATH=${LD_LIBRARY_PATH} \
    CPPFLAGS=${CPPFLAGS} LDFLAGS=${LDFLAGS} PATH=${PATH} \
    -- sh -c 'cd /tmp && mkdir -p "${INSTALL_PREFIX}" && \
    curl -o "${PYTHON_TGZ}" "https://www.python.org/ftp/python/${PYTHON_VERSION}/${PYTHON_TGZ}" && \
    tar zxf "${PYTHON_TGZ}" && \
    cd "${PYTHON_SRC_DIR}" && \
    ./configure --prefix="${INSTALL_PREFIX}" --enable-shared --enable-optimizations --with-lto && \
    make altinstall'

  # echo "Stripping debug symbols to reduce size..."
  # sudo -- sh -c '/usr/bin/strip "${INSTALL_PREFIX}/bin/python3.11" && \
  #   /usr/bin/strip "${INSTALL_PREFIX}/lib/libpython3.11.so.1.0"'

  # Install pip
  sudo PYTHON_VERSION=${PYTHON_VERSION} INSTALL_PREFIX=${INSTALL_PREFIX} \
    PYTHON_TGZ=${PYTHON_TGZ} PYTHON_SRC_DIR=${PYTHON_SRC_DIR} LD_LIBRARY_PATH=${LD_LIBRARY_PATH} \
    CPPFLAGS=${CPPFLAGS} LDFLAGS=${LDFLAGS} PATH=${PATH} \
    -- sh -c 'cd /tmp && curl -sS https://bootstrap.pypa.io/get-pip.py | "${INSTALL_PREFIX}/bin/python3.11"'

  export PYTHON311_PATH="${INSTALL_PREFIX}"
  export pip_bin=${PYTHON311_PATH}/bin/pip3.11
  export VIRTUAL_ENV_VERSION="20.24.4"
  # Pip modules install
  sudo pip_bin=${pip_bin} LD_LIBRARY_PATH=${LD_LIBRARY_PATH} -- sh -c '${pip_bin} install virtualenv=='${VIRTUAL_ENV_VERSION}' virtualenv-make-relocatable==0.0.1 mysqlclient==2.1.1'
  sudo pip_bin=${pip_bin} LD_LIBRARY_PATH=${LD_LIBRARY_PATH} -- sh -c '${pip_bin} install psycopg2==2.9.6 --global-option=build_ext --global-option="--pg-config=$PG_CONFIG"'
  sudo pip_bin=${pip_bin} LD_LIBRARY_PATH=${LD_LIBRARY_PATH} -- sh -c 'ln -fs ${pip_bin} $(dirname ${pip_bin})/pip'
  popd > /dev/null
}

function install_python39() {
  local PYTHON_VERSION=${1:-"3.9.16"}
  local INSTALL_PREFIX=$2
  local LD_LIBRARY_PATH=$3
  local CPPFLAGS=$4
  local LDFLAGS=$5
  pushd . > /dev/null

  cd $HOME
  local PYTHON_TGZ="Python-${PYTHON_VERSION}.tgz"
  local PYTHON_SRC_DIR="Python-${PYTHON_VERSION}"

  export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/lib/mit/bin:$PATH

  echo "Installing Python ${PYTHON_VERSION}..."
  sudo PYTHON_VERSION=${PYTHON_VERSION} INSTALL_PREFIX=${INSTALL_PREFIX} \
    PYTHON_TGZ=${PYTHON_TGZ} PYTHON_SRC_DIR=${PYTHON_SRC_DIR} LD_LIBRARY_PATH=${LD_LIBRARY_PATH} \
    CPPFLAGS=${CPPFLAGS} LDFLAGS=${LDFLAGS} PATH=${PATH} \
    -- sh -c 'cd /tmp && mkdir -p "${INSTALL_PREFIX}" && \
    curl -o "${PYTHON_TGZ}" "https://www.python.org/ftp/python/${PYTHON_VERSION}/${PYTHON_TGZ}" && \
    tar zxf "${PYTHON_TGZ}" && \
    cd "${PYTHON_SRC_DIR}" && \
    ./configure --prefix="${INSTALL_PREFIX}" --enable-shared --enable-optimizations --with-lto && \
    make altinstall'

  # echo "Stripping debug symbols to reduce size..."
  # sudo -- sh -c '/usr/bin/strip "${INSTALL_PREFIX}/bin/python3.9" && \
  #   /usr/bin/strip "${INSTALL_PREFIX}/lib/libpython3.9.so.1.0"'

  # Install pip
  sudo PYTHON_VERSION=${PYTHON_VERSION} INSTALL_PREFIX=${INSTALL_PREFIX} \
    PYTHON_TGZ=${PYTHON_TGZ} PYTHON_SRC_DIR=${PYTHON_SRC_DIR} LD_LIBRARY_PATH=${LD_LIBRARY_PATH} \
    CPPFLAGS=${CPPFLAGS} LDFLAGS=${LDFLAGS} PATH=${PATH} \
    -- sh -c 'cd /tmp && curl -sS https://bootstrap.pypa.io/get-pip.py | "${INSTALL_PREFIX}/bin/python3.9"'

  export PYTHON39_PATH="${INSTALL_PREFIX}"
  export pip_bin=${PYTHON39_PATH}/bin/pip3.9
  export VIRTUAL_ENV_VERSION="20.19.0"
  # Pip modules install
  sudo pip_bin=${pip_bin} LD_LIBRARY_PATH=${LD_LIBRARY_PATH} -- sh -c '${pip_bin} install virtualenv=='${VIRTUAL_ENV_VERSION}' virtualenv-make-relocatable==0.0.1 mysqlclient==2.1.1'
  sudo pip_bin=${pip_bin} LD_LIBRARY_PATH=${LD_LIBRARY_PATH} -- sh -c '${pip_bin} install psycopg2==2.9.6 --global-option=build_ext --global-option="--pg-config=$PG_CONFIG"'
  sudo pip_bin=${pip_bin} LD_LIBRARY_PATH=${LD_LIBRARY_PATH} -- sh -c 'ln -fs ${pip_bin} $(dirname ${pip_bin})/pip'
  popd > /dev/null
}

function install_python38() {
  local PYTHON_VERSION=${1:-"3.8.12"}
  local INSTALL_PREFIX=$2
  local LD_LIBRARY_PATH=$3
  local CPPFLAGS=$4
  local LDFLAGS=$5
  pushd . > /dev/null

  cd $HOME
  local PYTHON_TGZ="Python-${PYTHON_VERSION}.tgz"
  local PYTHON_SRC_DIR="Python-${PYTHON_VERSION}"

  export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/lib/mit/bin:$PATH

  echo "Installing Python ${PYTHON_VERSION}..."
  sudo PYTHON_VERSION=${PYTHON_VERSION} INSTALL_PREFIX=${INSTALL_PREFIX} \
    PYTHON_TGZ=${PYTHON_TGZ} PYTHON_SRC_DIR=${PYTHON_SRC_DIR} LD_LIBRARY_PATH=${LD_LIBRARY_PATH} \
    CPPFLAGS=${CPPFLAGS} LDFLAGS=${LDFLAGS} PATH=${PATH} \
    -- sh -c 'cd /tmp && mkdir -p "${INSTALL_PREFIX}" && \
    curl -o "${PYTHON_TGZ}" "https://www.python.org/ftp/python/${PYTHON_VERSION}/${PYTHON_TGZ}" && \
    tar zxf "${PYTHON_TGZ}" && \
    cd "${PYTHON_SRC_DIR}" && \
    ./configure --prefix="${INSTALL_PREFIX}" --enable-shared --enable-optimizations --with-lto && \
    make altinstall'

  # echo "Stripping debug symbols to reduce size..."
  # sudo -- sh -c '/usr/bin/strip "${INSTALL_PREFIX}/bin/python3.8" && \
  #   /usr/bin/strip "${INSTALL_PREFIX}/lib/libpython3.8.so.1.0"'

  export PYTHON38_PATH="${INSTALL_PREFIX}"
  export pip_bin=${PYTHON38_PATH}/bin/pip3.8
  export VIRTUAL_ENV_VERSION="20.24.4"
  # Pip modules install
  sudo pip_bin=${pip_bin} LD_LIBRARY_PATH=${LD_LIBRARY_PATH} -- sh -c '${pip_bin} install virtualenv=='${VIRTUAL_ENV_VERSION}' virtualenv-make-relocatable==0.0.1 mysqlclient==2.1.1'
  sudo pip_bin=${pip_bin} LD_LIBRARY_PATH=${LD_LIBRARY_PATH} -- sh -c '${pip_bin} install psycopg2==2.9.6 --global-option=build_ext --global-option="--pg-config=$PG_CONFIG"'
  sudo pip_bin=${pip_bin} LD_LIBRARY_PATH=${LD_LIBRARY_PATH} -- sh -c 'ln -fs ${pip_bin} $(dirname ${pip_bin})/pip'
  popd > /dev/null
}

function install_sqlite_python() {
  local DOCKEROS="${1:-ubuntu22}"
  local PYTHON_VERSION="${2:-3.11.12}"
  local INSTALL_PREFIX="/opt/python/${PYTHON_VERSION}"
  local SQLITE3_PATH="/opt/sqlite3"

  pushd . > /dev/null

  if [[ "$PYTHON_VERSION" == "$REQ_PYTHON311" ]]; then
    if [[ -z ${PYTHON311_PATH+x} ]]; then
      install_build_dependencies "$DOCKEROS"
      install_sqlite3 "$SQLITE3_PATH"
      export LD_LIBRARY_PATH="${INSTALL_PREFIX}/lib:${SQLITE3_PATH}/lib:${LD_LIBRARY_PATH}"
      export CPPFLAGS="-I${SQLITE3_PATH}/include"
      export LDFLAGS="-L${SQLITE3_PATH}/lib"
      install_python311 "$PYTHON_VERSION" "$INSTALL_PREFIX" "$LD_LIBRARY_PATH" "$CPPFLAGS" "$LDFLAGS"
    fi
  elif [[ "$PYTHON_VERSION" == "$REQ_PYTHON39" ]]; then
    if [[ -z ${PYTHON39_PATH+x} ]]; then
      install_build_dependencies "$DOCKEROS"
      install_sqlite3 "$SQLITE3_PATH"
      export LD_LIBRARY_PATH="${INSTALL_PREFIX}/lib:${SQLITE3_PATH}/lib:${LD_LIBRARY_PATH}"
      export CPPFLAGS="-I${SQLITE3_PATH}/include"
      export LDFLAGS="-L${SQLITE3_PATH}/lib"
      install_python39 "$PYTHON_VERSION" "$INSTALL_PREFIX" "$LD_LIBRARY_PATH" "$CPPFLAGS" "$LDFLAGS"
    fi
  elif [[ "$PYTHON_VERSION" == "$REQ_PYTHON38" ]]; then
    if [[ -z ${PYTHON38_PATH+x} ]]; then
      install_build_dependencies "$DOCKEROS"
      install_sqlite3 "$SQLITE3_PATH"
      export LD_LIBRARY_PATH="${INSTALL_PREFIX}/lib:${SQLITE3_PATH}/lib:${LD_LIBRARY_PATH}"
      export CPPFLAGS="-I${SQLITE3_PATH}/include"
      export LDFLAGS="-L${SQLITE3_PATH}/lib"
      install_python38 "$PYTHON_VERSION" "$INSTALL_PREFIX" "$LD_LIBRARY_PATH" "$CPPFLAGS" "$LDFLAGS"
    fi
  fi

  popd > /dev/null
}

function centos7_install() {
  local os=${1:-"centos7"}

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
      unzip \
      python3-devel \
      postgresql-devel'
    # Ensure pg_config is available
    export PG_CONFIG=$(which pg_config)
    if [ -z "$PG_CONFIG" ]; then
      echo "Error: pg_config not found. Ensure PostgreSQL development libraries are installed."
      exit 1
    fi
    echo "PG_CONFIG is set to $PG_CONFIG"
    # MySQLdb install
    sudo -- sh -c 'cd /tmp && curl -sSLO https://cloudera-build-us-west-1.vpc.cloudera.com/s3/ARTIFACTS/mysql80-community-release-el7-11.noarch.rpm && \
        rpm -ivh mysql80-community-release-el7-11.noarch.rpm && \
        yum install -y mysql-community-libs mysql-community-client-plugins mysql-community-common'
    # NODEJS 16 install
    # Upgrading to node-v16 because of the following CVE's in node-v14 "CVE-2021-3450, CVE-2021-44531, CVE-2023-32004, CVE-2023-32006"
    # Node-v20-LTS is not supported by old OS'es - Redhat7_ppc, Centos7, Ubuntu18, Sles12. So upgrading to node-v16
    sudo -- sh -c 'cd /tmp && curl -fsSL https://rpm.nodesource.com/setup_16.x | sudo bash - && \
        yum install -y nodejs npm'

    unset PYTHON38_PATH
    if [[ -z ${PYTHON38_PATH+x} ]]; then
      install_sqlite_python "$os" "$REQ_PYTHON38"
    fi
  fi
}

function redhat8_install() {
  local os=${1:-"redhat8"}

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
      ncurses-c++-libs \
      python3-devel \
      postgresql-devel'
    # Ensure pg_config is available
    export PG_CONFIG=$(which pg_config)
    if [ -z "$PG_CONFIG" ]; then
      echo "Error: pg_config not found. Ensure PostgreSQL development libraries are installed."
      exit 1
    fi
    echo "PG_CONFIG is set to $PG_CONFIG"
    # MySQLdb install
    sudo -- sh -c 'yum install -y python3-mysqlclient'
    # NODEJS 20 install
    sudo -- sh -c 'cd /tmp && curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash - && \
      yum install -y nodejs'

    if [[ -z ${PYTHON311_PATH+x} ]]; then
      install_sqlite_python "$os" "$REQ_PYTHON311"
    fi

    if [[ -z ${PYTHON39_PATH+x} ]]; then
      install_sqlite_python "$os" "$REQ_PYTHON39"
    fi

    if [[ -z ${PYTHON38_PATH+x} ]]; then
      install_sqlite_python "$os" "$REQ_PYTHON38"
    fi

  fi
}

function redhat8_arm64_install() {
  local os=${1:-"redhat8-arm64"}

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
    # NODEJS 20 install
    sudo -- sh -c 'cd /tmp && curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash - && \
      yum install -y nodejs'
    # Pip modules install

    if [[ -z ${PYTHON311_PATH+x} ]]; then
      install_sqlite_python "$os" "$REQ_PYTHON311"
    fi

    if [[ -z ${PYTHON39_PATH+x} ]]; then
      install_sqlite_python "$os" "$REQ_PYTHON39"
    fi

    if [[ -z ${PYTHON38_PATH+x} ]]; then
      install_sqlite_python "$os" "$REQ_PYTHON38"
    fi
  fi
}

function redhat9_install() {
  local os=${1:-"redhat9"}

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
      ncurses-c++-libs \
      postgresql-devel'
    # Ensure pg_config is available
    export PG_CONFIG=$(which pg_config)
    if [ -z "$PG_CONFIG" ]; then
      echo "Error: pg_config not found. Ensure PostgreSQL development libraries are installed."
      exit 1
    fi
    echo "PG_CONFIG is set to $PG_CONFIG"
    # MySQLdb install
    sudo -- sh -c 'yum install -y python3-mysqlclient'
    # NODEJS 20 install
    sudo -- sh -c 'cd /tmp && curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash - && \
      yum install -y nodejs'

    if [[ -z ${PYTHON311_PATH+x} ]]; then
      install_sqlite_python "$os" "$REQ_PYTHON311"
    fi

    if [[ -z ${PYTHON39_PATH+x} ]]; then
      install_sqlite_python "$os" "$REQ_PYTHON39"
    fi

    if [[ -z ${PYTHON38_PATH+x} ]]; then
      install_sqlite_python "$os" "$REQ_PYTHON38"
    fi
  fi
}

function sles12_install() {
  local os=${1:-"sles12"}

  if [[ $FORCEINSTALL -eq 1 ]]; then
    # pre-req install
    sudo -- sh -c 'zypper refresh'
    sudo -- sh -c 'zypper install -y cyrus-sasl-gssapi \
      cyrus-sasl-plain \
      java-11-openjdk \
      java-11-openjdk-devel \
      java-11-openjdk-headless \
      krb5-client pam_krb5 krb5-appl-clients krb5-plugin-kdb-ldap \
      libpcap \
      ncurses-devel \
      nmap \
      python3-devel \
      postgresql-server-devel \
      xmlsec1 xmlsec1-devel  xmlsec1-openssl-devel'
    # Ensure pg_config is available
    export PG_CONFIG=$(which pg_config)
    if [ -z "$PG_CONFIG" ]; then
      echo "Error: pg_config not found. Ensure PostgreSQL development libraries are installed."
      exit 1
    fi
    echo "PG_CONFIG is set to $PG_CONFIG"
    # MySQLdb install
    sudo -- sh -c 'zypper install -y libmysqlclient-devel libmysqlclient18 libmysqld18 libmysqld-devel'
    # NODEJS 16 install
    # Upgrading to node-v16 because of the following CVE's in node-v14 "CVE-2021-3450, CVE-2021-44531, CVE-2023-32004, CVE-2023-32006"
    # Node-v20-LTS is not supported by old OS'es - Redhat7_ppc, Centos7, Ubuntu18, Sles12. So upgrading to node-v16
    sudo -- sh -c 'zypper install -y npm14 nodejs14'

    unset PYTHON38_PATH
    if [[ -z ${PYTHON38_PATH+x} ]]; then
      install_sqlite_python "$os" "$REQ_PYTHON38"
    fi
  fi
}

function sles15_install() {
  local os=${1:-"sles15"}

  if [[ $FORCEINSTALL -eq 1 ]]; then
    # pre-req install
    sudo -- sh -c 'zypper refresh'
    sudo -- sh -c 'zypper install -y cyrus-sasl-gssapi \
      cyrus-sasl-plain \
      java-11-openjdk \
      java-11-openjdk-devel \
      java-11-openjdk-headless \
      krb5-client pam_krb5 krb5-plugin-kdb-ldap \
      libpcap1 \
      ncurses-devel \
      nmap \
      postgresql-server-devel \
      xmlsec1 xmlsec1-devel  xmlsec1-openssl-devel'
    # Ensure pg_config is available
    export PG_CONFIG=$(which pg_config)
    if [ -z "$PG_CONFIG" ]; then
      echo "Error: pg_config not found. Ensure PostgreSQL development libraries are installed."
      exit 1
    fi
    echo "PG_CONFIG is set to $PG_CONFIG"
    # MySQLdb install
    sudo -- sh -c 'zypper install -y libmariadb-devel mariadb-client python3-mysqlclient'
    # NODEJS 18 install
    sudo -- sh -c 'zypper install -y nodejs18 npm20'
    sudo -- sh -c 'rm -f /usr/local/bin/node && ln -s /usr/bin/node18 /usr/local/bin/node'
    sudo -- sh -c 'rm -f /usr/local/bin/npm && ln -s /usr/bin/npm20 /usr/local/bin/npm'

    if [[ -z ${PYTHON311_PATH+x} ]]; then
      install_sqlite_python "$os" "$REQ_PYTHON311"
    fi

    if [[ -z ${PYTHON39_PATH+x} ]]; then
      install_sqlite_python "$os" "$REQ_PYTHON39"
    fi

    if [[ -z ${PYTHON38_PATH+x} ]]; then
      install_sqlite_python "$os" "$REQ_PYTHON38"
    fi
  fi
}

function ubuntu18_install() {
  local os=${1:-"ubuntu18"}

  if [[ $FORCEINSTALL -eq 1 ]]; then
    # pre-req install
    sudo -- sh -c 'apt-get update'
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
        python3-dev \
        libpq-dev \
        zlibc'
    # Ensure pg_config is available
    export PG_CONFIG=$(which pg_config)
    if [ -z "$PG_CONFIG" ]; then
      echo "Error: pg_config not found. Ensure PostgreSQL development libraries are installed."
      exit 1
    fi
    echo "PG_CONFIG is set to $PG_CONFIG"
    # MySQLdb install
    # It is pre-installed
    # NODEJS 16 install
    # Upgrading to node-v16 because of the following CVE's in node-v14 "CVE-2021-3450, CVE-2021-44531, CVE-2023-32004, CVE-2023-32006"
    # Node-v20-LTS is not supported by old OS'es - Redhat7_ppc, Centos7, Ubuntu18, Sles12. So upgrading to node-v16
    sudo -- sh -c 'cd /tmp && curl -sL https://deb.nodesource.com/setup_16.x | sudo bash - && \
      apt -y install nodejs'

    if [[ -z ${PYTHON311_PATH+x} ]]; then
      install_sqlite_python "$os" "$REQ_PYTHON311"
    fi

    if [[ -z ${PYTHON39_PATH+x} ]]; then
      install_sqlite_python "$os" "$REQ_PYTHON39"
    fi

    if [[ -z ${PYTHON38_PATH+x} ]]; then
      install_sqlite_python "$os" "$REQ_PYTHON38"
    fi
  fi
}

function ubuntu20_install() {
  local os=${1:-"ubuntu20"}

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
        libpq-dev \
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
    # Ensure pg_config is available
    export PG_CONFIG=$(which pg_config)
    if [ -z "$PG_CONFIG" ]; then
      echo "Error: pg_config not found. Ensure PostgreSQL development libraries are installed."
      exit 1
    fi
    echo "PG_CONFIG is set to $PG_CONFIG"
    # MySQLdb install
    # It is pre-installed
    # NODEJS 20 install
    sudo -- sh -c 'apt-get install -y curl && \
      cd /tmp && curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && \
      apt-get install -y nodejs'

    unset PYTHON38_PATH
    if [[ -z ${PYTHON38_PATH+x} ]]; then
      install_sqlite_python "$os" "$REQ_PYTHON38"
    fi
  fi
}

function ubuntu22_install() {
  local os=${1:-"ubuntu22"}

  if [[ $FORCEINSTALL -eq 1 ]]; then
    sudo -- sh -c 'apt update'
    # Add deadsnakes PPA for Python 3.8
    sudo -- sh -c 'add-apt-repository ppa:deadsnakes/ppa -y'
    sudo -- sh -c 'apt update'
    # pre-req install
    sudo -- sh -c 'DEBIAN_FRONTEND=noninteractive apt -qq -y install  \
        krb5-user \
        krb5-kdc \
        krb5-config \
        libkrb5-dev'
    sudo -- sh -c "apt -y install \
        ldap-utils \
        libxmlsec1 \
        libxmlsec1-openssl \
        libpq-dev \
        netcat \
        nmap \
        openssl \
        sudo \
        tar \
        util-linux"
    # Ensure pg_config is available
    export PG_CONFIG=$(which pg_config)
    if [ -z "$PG_CONFIG" ]; then
      echo "Error: pg_config not found. Ensure PostgreSQL development libraries are installed."
      exit 1
    fi
    echo "PG_CONFIG is set to $PG_CONFIG"
    # MySQLdb install
    # It is pre-installed
    # NODEJS 20 install
    sudo -- sh -c 'apt-get install -y curl && \
      cd /tmp && curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && \
      apt-get install -y nodejs'

    unset PYTHON311_PATH
    if [[ -z ${PYTHON311_PATH+x} ]]; then
      install_sqlite_python "$os" "$REQ_PYTHON311"
    fi

    if [[ -z ${PYTHON39_PATH+x} ]]; then
      install_sqlite_python "$os" "$REQ_PYTHON39"
    fi

    unset PYTHON38_PATH
    if [[ -z ${PYTHON38_PATH+x} ]]; then
      install_sqlite_python "$os" "$REQ_PYTHON38"
    fi
  fi
}

function ubuntu24_install() {
  local os=${1:-"ubuntu24"}

  if [[ $FORCEINSTALL -eq 1 ]]; then
    sudo -- sh -c 'apt update'
    # pre-req install
    sudo -- sh -c 'DEBIAN_FRONTEND=noninteractive apt -qq -y install  \
        krb5-user \
        krb5-kdc \
        krb5-config \
        libkrb5-dev'
    sudo -- sh -c "apt -y install \
        ldap-utils \
        libxmlsec1 \
        libxmlsec1-openssl \
        libpq-dev \
        netcat-openbsd \
        nmap \
        openssl \
        sudo \
        tar \
        util-linux"
    # Ensure pg_config is available
    export PG_CONFIG=$(which pg_config)
    if [ -z "$PG_CONFIG" ]; then
      echo "Error: pg_config not found. Ensure PostgreSQL development libraries are installed."
      exit 1
    fi
    echo "PG_CONFIG is set to $PG_CONFIG"
    # MySQLdb install
    # It is pre-installed

    # NODEJS 20 install
    # Force curl to use system libraries to avoid conflicts from /usr/local/lib
    sudo -- sh -c 'export LD_LIBRARY_PATH="/usr/lib/$(uname -m)-linux-gnu:/usr/lib64:/usr/lib:$LD_LIBRARY_PATH"; \
      apt-get install -y curl && \
      cd /tmp && curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
      apt-get install -y nodejs'

    unset PYTHON311_PATH
    if [[ -z ${PYTHON311_PATH+x} ]]; then
      install_sqlite_python "$os" "$REQ_PYTHON311"
    fi
  fi
}
