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
export HUE_HOME_DIR=$(dirname $(dirname "$SCRIPT_DIR"))

source $SCRIPT_DIR/python/python_helper.sh
PYTHON_BIN="${VENV_BIN_PATH}/python"
HUE="${VENV_BIN_PATH}/hue"

echo "Hue Environment Variables:" 1>&2
env 1>&2

function set_path() {
   etpath=$(dirname $2)
   if [ "$1" == "PYTHONPATH" ]; then
     if [ -z ${PYTHONPATH:+x} ]; then
       export PYTHONPATH=$etpath
     else
       export PYTHONPATH=$PYTHONPATH:$etpath
     fi
   elif [ "$1" == "LD_LIBRARY_PATH" ]; then
     if [ -z ${LD_LIBRARY_PATH:+x} ]; then
       export LD_LIBRARY_PATH=$etpath
     else
       export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$etpath
     fi
   elif [ "$1" == "PATH" ]; then
     if [ -z ${PATH:+x} ]; then
       export PATH=$etpath
     else
       export PATH=$PATH:$etpath
     fi
   fi
}

# This function sets the ENVIRONMENT variable, it has 3 args
# 1. target file, 2. environment variable name
# 3. list of possible places where target can be found
# It iterates over list and tries matching list item and target
# on the filesystem.
function set_env_var() {
  target=$1
  shift
  setvar=$1
  shift
  search=("$@")
  targetpath=""

  # Dont use "echo" in the function as last line returns value
  for spath in ${search[@]}; do
    tpath=""
    if echo x"$target" | grep '*' > /dev/null || \
       echo x"$spath"  | grep '*' > /dev/null; then
      # sort with newone first
      glob_path=$(ls -1td $spath/$target 2>/dev/null|head -1)
      if [ -z ${glob_path:+x} ]; then
        tpath=""
      else
        tpath=$glob_path
      fi
    else
      if [ -e "$spath/$target" ]; then
        tpath="$spath/$target"
      fi
    fi
    if [ "$tpath" != "" ]; then
      targetpath=$tpath
      set_path $setvar $targetpath
      break
    fi
  done
  echo $targetpath
}

add_postgres_to_pythonpath_for_version() {
  local version="${1:-$SELECTED_PYTHON_VERSION}"  # Use first arg if provided, otherwise use SELECTED_PYTHON_VERSION
  
  # If postgres engine is detected in *.ini files then check for proper psycopg2 version.
  if grep -q '^\s*engine\s*=\s*postgres\+' *.ini; then
    list=("/usr/lib*" "/usr/local/lib/python${version}/*-packages" \
          "/usr/lib64/python${version}/*-packages" \
          "/opt/rh/rh-postgresql*/root/usr/lib64" \
          "/usr/pgsql-*/lib" \
          )
    set_env_var "libpq.so" "LD_LIBRARY_PATH" "${list[@]}"

    list=("/usr/bin" "/opt/rh/rh-python${version//./}/root/usr/local/lib64/python${version}/site-packages" \
          "/usr/local/lib/python${version}/*-packages" \
          "/usr/lib64/python${version}/*-packages" \
          )
    set_env_var "psycopg2" "PYTHONPATH" "${list[@]}"
  fi
}

add_mysql_to_pythonpath_for_version() {
  local version="${1:-$SELECTED_PYTHON_VERSION}"  # Use first arg if provided, otherwise use SELECTED_PYTHON_VERSION
  
  # If mysql engine is detected in *.ini files then check for proper MySQL-python version.
  if grep -q '^\s*engine\s*=\s*mysql\+' *.ini; then
    if [ -z ${LD_LIBRARY_PATH:+x} ]; then
      list=("/usr/lib*" "/usr/local/lib/python${version}/*-packages" \
            "/usr/lib64/python${version}/*-packages" \
            "/opt/rh/rh-mysql*/root/usr/lib64" \
            "/usr/lib64/mysql" \
            )
      set_env_var "libmysqlclient.so" "LD_LIBRARY_PATH" "${list[@]}"
    else
      echo "LD_LIBRARY_PATH is taken from safety valve, $LD_LIBRARY_PATH"
    fi

    if [ -z ${PYTHONPATH:+x} ]; then
      # If we've included a MySQL-python for this platform, override on PYTHONPATH
      list=("/usr/bin" "/opt/rh/rh-python${version//./}/root/usr/local/lib64/python${version}/site-packages" \
            "/usr/local/lib/python${version}/*-packages" \
            "/usr/lib64/python${version}/*-packages" \
            )
      set_env_var "MySQLdb" "PYTHONPATH" "${list[@]}"
    else
      echo "PYTHONPATH is taken from safety valve, $PYTHONPATH"
    fi
  fi
}

add_postgres_to_pythonpath_for_version "$SELECTED_PYTHON_VERSION"
add_mysql_to_pythonpath_for_version "$SELECTED_PYTHON_VERSION"


# Executes Django database migrations with retry logic to handle
# concurrent migration attempts from multiple hosts.
function run_syncdb_and_migrate_subcommands() {
  # Run the initial command first, but allow it to fail gracefully
  echo "INFO: Running --fake-initial to sync history for legacy databases..."
  if ! $HUE migrate --fake-initial --noinput; then
    echo "WARN: --fake-initial failed, but continuing with regular migration..."
  fi

  # Now, attempt the main migration in a retry loop.
  local max_attempts=3
  local delay_seconds=5

  for ((attempt=1; attempt<=max_attempts; attempt++)); do
    echo "INFO: Applying migrations (Attempt $attempt of $max_attempts)..."

    # If the migrate command succeeds, we're done.
    if $HUE migrate --noinput; then
      echo "INFO: Migration successful."
      return 0
    fi

    # If we've not reached the max attempts, wait and retry.
    if [ $attempt -lt $max_attempts ]; then
      echo "WARN: Migration failed, likely due to a temporary lock. Retrying in $delay_seconds seconds..."
      sleep $delay_seconds
    fi
  done

  # If the loop finishes, all attempts have failed.
  echo "ERROR: All migration attempts failed after $max_attempts tries." >&2
  exit 1
}

if [[ "$1" == "kt_renewer" ]]; then
  # The Kerberos ticket renewer needs to know where kinit is.
  if [ -d /usr/kerberos/bin ]; then
    export PATH=/usr/kerberos/bin:$PATH
  fi
  KINIT_PATH=`which kinit`
  KINIT_PATH=${KINIT_PATH-/usr/bin/kinit}
  perl -pi -e "s#\{\{KINIT_PATH}}#$KINIT_PATH#g" $HUE_CONF_DIR/*.ini
fi

if [[ "dumpdata" == "$1" ]]; then
  umask 037
  "$HUE" "$1" --indent 2 > "$2"
elif [[ "syncdb" == "$1" ]]; then
  run_syncdb_and_migrate_subcommands
elif [[ "ldaptest" == "$1" ]]; then
  "$HUE" "$1"
elif [[ "runcpserver" == "$1" ]]; then
  run_syncdb_and_migrate_subcommands
  exec "$HUE" "runcpserver"
elif [[ "rungunicornserver" == "$1" ]]; then
  run_syncdb_and_migrate_subcommands
  exec "$HUE" "rungunicornserver"
else
  exec "$HUE" "$@"
fi
