#!/bin/bash
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -e

usage() {
  echo "
  Make a Hue installation relocatable. Run this in the installation
  directory created by 'make install', before you relocate it.
  Usage:
      $0
  "
  exit 1
}

if [ $# != 0 ] ; then
  usage
fi

find_os() {
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

find_home() {
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

# We're in <hue_root>/tools
CURR_DIR=$(find_home)

if [[ $CURR_DIR == */hue ]]; then
  HUE_ROOT=$CURR_DIR
elif [[ $CURR_DIR == */tools ]]; then
  HUE_ROOT=$(dirname $CURR_DIR)
fi

ENV_PYTHON="$HUE_ROOT/build/env/bin/python"
VIRTUAL_BOOTSTRAP="$CURR_DIR/virtual-bootstrap/virtual-bootstrap.py"

if [[ ! -e $ENV_PYTHON ]]; then
  echo "Is $ENV_PYTHON available?"
  echo "Failing to perform relocataion"
  exit 127
fi

if [[ ! -e $VIRTUAL_BOOTSTRAP ]]; then
  echo "Is $VIRTUAL_BOOTSTRAP available?"
  echo "Failing to perform relocataion"
  exit 127
fi

export PATH=$(dirname $ENV_PYTHON):$PATH

PYVER=$($ENV_PYTHON -V 2>&1|head -c 10)
# Step 1. Fix virtualenv
if [[ $PYVER == "Python 3.8" ]]; then
  pushd .
  cd $HUE_ROOT
  virtualenv-make-relocatable "build/env"
  $ENV_PYTHON $VIRTUAL_BOOTSTRAP --relocatable_pth "build/env"
  popd
elif [[ $PYVER == "Python 2.7" ]]; then
  if [ -e "$HUE_ROOT/tools/enable-python27.sh" ]; then
    source $HUE_ROOT/tools/enable-python27.sh
  fi

  $ENV_PYTHON $VIRTUAL_BOOTSTRAP --relocatable "$HUE_ROOT/build/env"
fi

# Step 1b. Fix any broken lib64 directory
LIB64="$HUE_ROOT/build/env/lib64"
if [ -L "$LIB64" -a ! -e "$LIB64" ] ; then
  rm "$LIB64"
  ln -s lib "$LIB64"
fi

# Step 2. Fix .ini symlinks for all apps (make them relative)
for app in $HUE_ROOT/apps/* ; do
  if [ -d "$app/conf" ] ; then
    appname=$(basename $app)
    pushd "$HUE_ROOT/desktop/conf"
    ln -sfv ../../apps/$appname/conf/*.ini .
    popd
  fi
done

# Step 3. Clean up any old .pyc files
find "$HUE_ROOT" . -name "*.pyc" -exec rm -f {} \;
