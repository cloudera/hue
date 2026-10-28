#!/usr/bin/env bash
set -ex

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

WORK_DIR=$(find_home)
. "${WORK_DIR}/build_hue_common.sh"

BUILDTYPE=$1
DOCKEROS=$2
HUE_JAR_VERSION=$3

# All Cloudera packaging targets build Hue with Python 3.11 (see Makefile.vars).
PYTHON311_OSES=(
  "centos7" "redhat8" "redhat8-arm64" "redhat9" "redhat9-arm64"
  "sles12" "sles15" "ubuntu18" "ubuntu20" "ubuntu22" "ubuntu24"
)

# 3.11.18 is the first 3.11 release that rejects the compromised eMudhra intermediate CAs.
export REQ_PYTHON311="3.11.18"

export DESKTOP_VERSION=$DOCKEROS
export HUE_WEBPACK_CONFIG='webpack.config.internal.js'
export SQLITE3_PATH=${SQLITE3_PATH:="${TOOLS_HOME}/sqlite/bin/sqlite3"}
export ORACLE_INSTANTCLIENT19_PATH="/opt/toolchain/instantclient_19_15"
export LD_LIBRARY_PATH="/usr/local/lib:$ORACLE_INSTANTCLIENT19_PATH:$LD_LIBRARY_PATH"
export LD_RUN_PATH="/usr/local/lib:$ORACLE_INSTANTCLIENT19_PATH:$LD_RUN_PATH"
export ORIGINAL_PATH=$PATH

setup_python_env() {
  local os="$1"

  if is_supported_os PYTHON311_OSES "$os"; then
    export PYTHON311_PATH=${PYTHON311_PATH:=/opt/python/3.11.18}
    if is_supported_python_version "$PYTHON311_PATH/bin/python3.11" $REQ_PYTHON311; then
      export PATH="$PYTHON311_PATH/bin:$PATH"
    else
      unset PYTHON311_PATH
    fi
  fi
}

install_prerequisite() {
  local os="$1"

  case "$os" in
    centos7) centos7_install "$os";;
    redhat8|snapshot) redhat8_install "$os";;
    redhat9) redhat9_install "$os";;
    sles12) sles12_install "$os";;
    sles15) sles15_install "$os";;
    ubuntu18) ubuntu18_install "$os";;
    ubuntu20) ubuntu20_install "$os";;
    ubuntu22) ubuntu22_install "$os";;
    ubuntu24) ubuntu24_install "$os";;
    redhat8-arm64) redhat8_arm64_install "$os";;
    redhat9-arm64) redhat9_arm64_install "$os";;
    *) echo "Unsupported OS: $os"; exit 1 ;;
  esac

  export SQLITE3_PATH=${SQLITE3_PATH:-"$TOOLS_HOME/sqlite/bin/sqlite3"}
}

should_build_python() {
  local os="$1"
  is_supported_os PYTHON311_OSES "$os"
}

setup_python_env "$DOCKEROS"

big_console_header "Hue PreRequisite Start for $DOCKEROS"
install_prerequisite "$DOCKEROS"
big_console_header "Hue PreRequisite End for $DOCKEROS"

if should_build_python "$DOCKEROS"; then
  HUE_SRC=$(realpath "$WORK_DIR/../..")
  cd "$HUE_SRC" || exit 1

  BLD_DIR="${BLD_DIR:-$HUE_SRC/build}"
  BLD_DIR_ENV="$BLD_DIR/env"
  echo "BLD_DIR_ENV=${BLD_DIR_ENV}"

  export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${ORACLE_INSTANTCLIENT19_PATH}
  export PATH="${PYTHON311_PATH:+$PYTHON311_PATH/bin:}/opt/sqlite3/bin:/usr/bin:$ORIGINAL_PATH"

  big_console_header "Hue Build Start for python3.11" "$@"
  BLD_DIR_ENV="$BLD_DIR_ENV" PYTHON_VER="python3.11" make apps docs
  BLD_DIR_ENV="$BLD_DIR_ENV" PYTHON_VER="python3.11" make relocatable-env
  BLD_DIR_ENV="$BLD_DIR_ENV" PYTHON_VER="python3.11" make huecheck
  big_console_header "Hue Build End for python3.11" "$@"
fi

big_console_header "Hue PROD Build Start for" "$@"
PYTHON_VER="python3.11" make release
big_console_header "Hue PROD Build End for" "$@"
