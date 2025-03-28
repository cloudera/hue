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

# wrapper script to identify the latest python and pass the execution
# to the corresponding hue script in the `build` directory.

set -ex

# Time marker for both stderr and stdout
date; date 1>&2

export SCRIPT_DIR=`dirname $0`
HUE_PARCEL_DIR=$(dirname $(dirname "$SCRIPT_DIR"))

source $SCRIPT_DIR/python/python_helper.sh

function stop_previous_hueprocs() {
  for p in $(cat /tmp/hue_${HUE_PORT}.pid); do
    if [[ $p -eq $(ps -p $p -ho pid=) ]]; then
      kill -9 $p
    fi
  done
}


HUE="${HUE_PARCEL_DIR}/$(latest_venv_bin_path)/hue"

if [[ "dumpdata" == "$1" ]]; then
  umask 037
  "$HUE" "$1" --indent 2 > "$2"
elif [[ "syncdb" == "$1" ]]; then
  run_syncdb_and_migrate_subcommands
elif [[ "ldaptest" == "$1" ]]; then
  "$HUE" "$1"
elif [[ "runcpserver" == "$1" ]]; then
  exec "$HUE" "runcpserver"
elif [[ "rungunicornserver" == "$1" ]]; then
  stop_previous_hueprocs
  exec "$HUE_LOGLISTENER" &
  echo $! > /tmp/hue_${HUE_PORT}.pid
  exec "$HUE" "rungunicornserver"
else
  exec "$HUE" "$@"
fi
