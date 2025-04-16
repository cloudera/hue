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
  if [[ $1 == "redhat9_ppc" ]]; then
    export FORCEINSTALL=0
    export SQLITE3_PATH="$TOOLS_HOME/sqlite/bin/sqlite3"
    redhat9_ppc_install
  elif [[ $1 == "redhat8_ppc" ]]; then
    export FORCEINSTALL=0
    export SQLITE3_PATH="$TOOLS_HOME/sqlite/bin/sqlite3"
    redhat8_ppc_install
  elif [[ $1 == "redhat7_ppc" ]]; then
    export FORCEINSTALL=0
    export SQLITE3_PATH="$TOOLS_HOME/sqlite/bin/sqlite3"
    redhat7_ppc_install
  fi

  export SQLITE3_PATH=${SQLITE3_PATH:-"$TOOLS_HOME/sqlite/bin/sqlite3"}
  # check_sqlite3
  if [[ $1 == "centos7" ]]; then
    export PYTHON38_PATH=/opt/cloudera/cm-agent
    export pip38_bin="$PYTHON38_PATH/bin/pip3.8"
    centos7_install
  elif [[ $1 == "redhat8" || $1 == "snapshot" ]]; then
    redhat8_install
  elif [[ $1 == "sles12" ]]; then
    sles12_install
    export PATH=/usr/lib/mit/bin:$PATH
  elif [[ $1 == "sles15" ]]; then
    sles15_install
    export PATH=/usr/lib/mit/bin:$PATH
  elif [[ $1 == "ubuntu18" ]]; then
    ubuntu18_install
  elif [[ $1 == "ubuntu20" ]]; then
    ubuntu20_install
  elif [[ $1 == "redhat9" ]]; then
    redhat9_install
  elif [[ $1 == "ubuntu22" ]]; then
    ubuntu22_install
  elif [[ $1 == "redhat8-arm64" ]]; then
    redhat8_arm64_install
  fi

}

WORK_DIR=$(find_home)
. ${WORK_DIR}/build_hue_common.sh

BUILDTYPE=$1
DOCKEROS=$2
HUE_JAR_VERSION=$3

export VIRTUAL_ENV_VERSION="20.24.4"
export VIRTUAL_ENV_RELOCATABLE_VERSION="0.0.1"

export DESKTOP_VERSION=$2
export HUE_WEBPACK_CONFIG='webpack.config.internal.js'
export PATH="$PYTHON38_PATH/bin:$PATH"
export SYS_PYTHON="$PYTHON38_PATH/bin/python3.8"
export SYS_PIP="$PYTHON38_PATH/bin/pip3.8"
export SQLITE3_PATH=${SQLITE3_PATH:="${TOOLS_HOME}/sqlite/bin/sqlite3"}
export ORACLE_INSTANTCLIENT19_PATH="/opt/toolchain/instantclient_19_15"
export LD_LIBRARY_PATH=/usr/local/lib:$ORACLE_INSTANTCLIENT19_PATH:$LD_LIBRARY_PATH
export LD_RUN_PATH=/usr/local/lib:$ORACLE_INSTANTCLIENT19_PATH:$LD_RUN_PATH

PYTHON_VERSIONS=("python3.11" "python3.9" "python3.8")
for PYTHON_VER in "${PYTHON_VERSIONS[@]}"; do
  if [[ $PYTHON_VER == "python3.8" && ( $DOCKEROS == "redhat7_ppc" || $DOCKEROS == "redhat8" || $DOCKEROS == "redhat8_ppc" || $DOCKEROS == "sles12" || $DOCKEROS == "centos7" || $DOCKEROS == "ubuntu18" || $DOCKEROS == "ubuntu20" || $DOCKEROS == "ubuntu22" ) ]]; then
    check_python38_path
    export PATH="$PYTHON38_PATH/bin:$PATH"
    export SYS_PYTHON="$PYTHON38_PATH/bin/python3.8"
    export SYS_PIP="$PYTHON38_PATH/bin/pip3.8"
    export VIRTUAL_ENV_VERSION="20.24.4"
  elif [[ $PYTHON_VER == "python3.9" && ( $DOCKEROS == "redhat9" || $DOCKEROS == "redhat8" || $DOCKEROS == "redhat9_ppc" || $DOCKEROS == "redhat8-arm64" ) ]]; then
    check_python39_path
    export PATH="$PYTHON39_PATH/bin:$PATH"
    export SYS_PYTHON="$PYTHON39_PATH/bin/python3.9"
    export SYS_PIP="$PYTHON39_PATH/bin/pip3.9"
    export VIRTUAL_ENV_VERSION="20.19.0"
  elif [[ $PYTHON_VER == "python3.11" && ( $DOCKEROS == "redhat9" || $DOCKEROS == "redhat8" || $DOCKEROS == "sles15" || $DOCKEROS == "redhat8-arm64" ) ]]; then
    check_python311_path
    export PATH="$PYTHON311_PATH/bin:$PATH"
    export SYS_PYTHON="$PYTHON311_PATH/bin/python3.11"
    export SYS_PIP="$PYTHON311_PATH/bin/pip3.11"
    export VIRTUAL_ENV_VERSION="20.24.4"
  else
    continue
  fi

  big_console_header "Hue PreRequisite Start for" $PYTHON_VER "$@"
  install_prerequisite $DOCKEROS
  big_console_header "Hue PreRequisite End for" $PYTHON_VER "$@"

  HUE_SRC=$(realpath "$WORK_DIR/../..")
  cd "$HUE_SRC" || exit 1

  BLD_DIR="${BLD_DIR:-build}"             # Default build directory if not set
  if [[ $PYTHON_VER == "python3.11" ]]; then
    BLD_DIR_ENV="${BLD_DIR}/env"
  else
    BLD_DIR_ENV="${BLD_DIR}/venvs/${PYTHON_VER}"
  fi
  echo "BLD_DIR_ENV=${BLD_DIR_ENV}"

  big_console_header "Hue Build Start for" $PYTHON_VER "$@"
  PYTHON_VER=$PYTHON_VER make apps docs relocatable-env huecheck
  big_console_header "Hue Build End for" $PYTHON_VER "$@"
done
big_console_header "Hue PROD Build Start for" "$@"
make release
big_console_header "Hue PROD Build End for" "$@"
