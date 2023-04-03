#!/usr/bin/env bash

set -ex

# Time marker for both stderr and stdout
date; date 1>&2

FORCEINSTALL=1

function find_os() {
  unameOut="$(uname -s)"
  case "${unameOut}" in
    Linux*)     machine=Linux;;
    Darwin*)    machine=Mac;;
    CYGWIN*)    machine=Cygwin;;
    MINGW*)     machine=MinGw;;
    *)          machine="UNKNOWN:${unameOut}"
  esac
  echo ${machine}
}

function find_home() {
  runningos=$(find_os)
  WORK_DIR=""
  if [[ ${runningos} == "Linux" ]]; then
    WORK_DIR=$(dirname "$(readlink -f "$0" || echo "$argv0")")
  elif [[ ${runningos} == "Mac" ]]; then
    WORK_DIR="$( cd "$( dirname "$argv0" )" && pwd )"
  else
    echo "Not Supported " $runningos
    exit 1
  fi
  echo ${WORK_DIR}
}

function install_prerequisite() {
  if [[ $1 == "redhat8_ppc" ]]; then
    export FORCEINSTALL=0
    export SQLITE3_PATH="$TOOLS_HOME/sqlite/bin/sqlite3"
    redhat8_ppc_install
  elif [[ $1 == "redhat7_ppc" ]]; then
    export FORCEINSTALL=0
    export SQLITE3_PATH="$TOOLS_HOME/sqlite/bin/sqlite3"
    redhat7_ppc_install
    source /opt/rh/rh-nodejs14/enable
  fi

  export SQLITE3_PATH=${SQLITE3_PATH:-"$TOOLS_HOME/sqlite/sqlite3"}
  check_python_path
  check_sqlite3
  if [[ $1 == "centos7" ]]; then
    export PYTHON38_PATH=/opt/cloudera/cm-agent
    export pip38_bin="$PYTHON38_PATH/bin/pip3.8"
    centos7_install
    source /opt/rh/rh-nodejs14/enable
  elif [[ $1 == "redhat8" ]]; then
    redhat8_install
  elif [[ $1 == "sles12" ]]; then
    sles12_install
    export PATH=/usr/lib/mit/bin:$PATH
  elif [[ $1 == "ubuntu18" ]]; then
    ubuntu18_install
  elif [[ $1 == "ubuntu20" ]]; then
    ubuntu20_install
  fi

}

WORK_DIR=$(find_home)
. ${WORK_DIR}/build_hue_common.sh

BUILDTYPE=$1
DOCKEROS=$2
HUE_JAR_VERSION=$3

big_console_header "Hue PreRequisite Start" "$@"
install_prerequisite $DOCKEROS
big_console_header "Hue PreRequisite End" "$@"

export DESKTOP_VERSION=$2
export HUE_WEBPACK_CONFIG='webpack.config.internal.js'
export PYTHON_H=$PYTHON38_PATH/include/python3.8/Python.h
export PYTHON_VER=python3.8
export SYS_PYTHON=$PYTHON38_PATH/bin/python3.8
export SQLITE3_PATH=${SQLITE3_PATH:="${TOOLS_HOME}/sqlite/sqlite3"}
export ORACLE_INSTANTCLIENT19_PATH="/opt/toolchain/instantclient_19_15"
export LD_LIBRARY_PATH=/usr/local/lib:$ORACLE_INSTANTCLIENT19_PATH:$LD_LIBRARY_PATH
export LD_RUN_PATH=/usr/local/lib:$ORACLE_INSTANTCLIENT19_PATH:$LD_RUN_PATH
export PATH=$HOME/.local/bin:$PYTHON38_PATH/bin:${TOOLS_HOME}/sqlite:/usr/bin:$PATH

HUE_SRC=$(realpath $WORK_DIR/../..)
export ROOT=$HUE_SRC
cd $HUE_SRC

big_console_header "Hue Build Start" "$@"
make apps docs
bash -x ./tools/relocatable.sh
make prod
big_console_header "Hue Build End" "$@"
