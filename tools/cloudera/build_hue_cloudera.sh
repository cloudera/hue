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

PYTHON38_OSES=("centos7" "redhat8" "sles12" "ubuntu20" "ubuntu22")
PYTHON39_OSES=("redhat8" "redhat8-arm64" "redhat9")
PYTHON311_OSES=("redhat8" "redhat8-arm64" "redhat9" "sles15" "ubuntu22" "ubuntu24")

LATEST_PYTHON="python3.11"
PYTHON_VERSIONS=("python3.11" "python3.9" "python3.8")

export REQ_PYTHON38="3.8.12"
export REQ_PYTHON39="3.9.16"
export REQ_PYTHON311="3.11.12"

export DESKTOP_VERSION=$DOCKEROS
export HUE_WEBPACK_CONFIG='webpack.config.internal.js'
export SQLITE3_PATH=${SQLITE3_PATH:="${TOOLS_HOME}/sqlite/bin/sqlite3"}
export ORACLE_INSTANTCLIENT19_PATH="/opt/toolchain/instantclient_19_15"
export LD_LIBRARY_PATH="/usr/local/lib:$ORACLE_INSTANTCLIENT19_PATH:$LD_LIBRARY_PATH"
export LD_RUN_PATH="/usr/local/lib:$ORACLE_INSTANTCLIENT19_PATH:$LD_RUN_PATH"
export ORIGINAL_PATH=$PATH

setup_python_env() {
  local ver="$1" os="$2"

  case "$ver" in
    python3.8)
      if is_supported_os PYTHON38_OSES "$os"; then
        export PYTHON38_PATH=${PYTHON38_PATH:=/opt/python/3.8.12}
        if is_supported_python_version "$PYTHON38_PATH/bin/python3.8" $REQ_PYTHON38; then
          export PATH="$PYTHON38_PATH/bin:$PATH"
        else
          unset PYTHON38_PATH
        fi
      fi
      ;;
    python3.9)
      if is_supported_os PYTHON39_OSES "$os"; then
        export PYTHON39_PATH=${PYTHON39_PATH:=/opt/python/3.9.16}
        if is_supported_python_version "$PYTHON39_PATH/bin/python3.9" $REQ_PYTHON39; then
          export PATH="$PYTHON39_PATH/bin:$PATH"
        else
          unset PYTHON39_PATH
        fi
      fi
      ;;
    python3.11)
      if is_supported_os PYTHON311_OSES "$os"; then
        export PYTHON311_PATH=${PYTHON311_PATH:=/opt/python/3.11.12}
        if is_supported_python_version "$PYTHON311_PATH/bin/python3.11" $REQ_PYTHON311; then
          export PATH="$PYTHON311_PATH/bin:$PATH"
        else
          unset PYTHON311_PATH
        fi
      fi
      ;;
    *) echo "Unsupported python version: $ver"; exit 1 ;;
  esac
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
    *) echo "Unsupported OS: $os"; exit 1 ;;
  esac

  export SQLITE3_PATH=${SQLITE3_PATH:-"$TOOLS_HOME/sqlite/bin/sqlite3"}
}

should_build_python() {
  local ver="$1"
  local os="$2"

  case "$ver" in
    python3.11)
      is_supported_os PYTHON311_OSES "$os"
      return $?
      ;;
    python3.9)
      is_supported_os PYTHON39_OSES "$os"
      return $?
      ;;
    python3.8)
      is_supported_os PYTHON38_OSES "$os"
      return $?
      ;;
    *)
      return 1
      ;;
  esac

  return 1
}

for PYTHON_VER in "${PYTHON_VERSIONS[@]}"; do
  setup_python_env "$PYTHON_VER" "$DOCKEROS"
done

big_console_header "Hue PreRequisite Start for $DOCKEROS"
install_prerequisite "$DOCKEROS"
big_console_header "Hue PreRequisite End for $DOCKEROS"

THISPATH=$PATH
for PYTHON_VER in "${PYTHON_VERSIONS[@]}"; do
  HUE_SRC=$(realpath "$WORK_DIR/../..")
  cd "$HUE_SRC" || exit 1

  if should_build_python "$PYTHON_VER" "$DOCKEROS"; then
    BLD_DIR="${BLD_DIR:-$HUE_SRC/build}"
    BLD_DIR_ENV="$BLD_DIR/venvs/${PYTHON_VER}"
    [[ "$PYTHON_VER" == "python3.11" || "$DOCKEROS" =~ (sles12|centos7|ubuntu20) ]] && BLD_DIR_ENV="$BLD_DIR/env"
    echo "BLD_DIR_ENV=${BLD_DIR_ENV}"

    export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${ORACLE_INSTANTCLIENT19_PATH}
    export PATH=$PYTHON38_PATH/bin:$PYTHON39_PATH/bin:$PYTHON311_PATH/bin:/opt/sqlite3/bin:/usr/bin:$THISPATH

    big_console_header "Hue Build Start for" "$PYTHON_VER" "$@"
    BLD_DIR_ENV="$BLD_DIR_ENV" PYTHON_VER="$PYTHON_VER" make apps docs
    BLD_DIR_ENV="$BLD_DIR_ENV" PYTHON_VER="$PYTHON_VER" make relocatable-env
    BLD_DIR_ENV="$BLD_DIR_ENV" PYTHON_VER="$PYTHON_VER" make huecheck
    big_console_header "Hue Build End for" "$PYTHON_VER" "$@"
  fi
done

big_console_header "Hue PROD Build Start for" "$@"
if [[ "$DOCKEROS" =~ (centos7|sles12|ubuntu18) ]]; then
  PYTHON_VER="python3.8" make release
else
  PYTHON_VER="python3.11" make release
fi
big_console_header "Hue PROD Build End for" "$@"
