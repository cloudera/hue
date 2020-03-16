#!/bin/bash
# Copyright (c) 2019 Cloudera, Inc. All rights reserved.

set -x

# Time marker for both stderr and stdout
date; date 1>&2

export DESKTOP_LOG_DIR="/var/log/hive"
export PYTHON_EGG_CACHE=$HUE_CONF_DIR/.python-eggs
export SERVER_SOFTWARE="apache"

function prepare_huedb() {
  (
  flock -x 124
  $HUE_BIN/hue syncdb --noinput
  $HUE_BIN/hue makemigrations --noinput --merge
  $HUE_BIN/hue migrate
  ) 124>$HUE_CONF_DIR/hue.lock
}

function db_connectivity_check() {
  i=1
  ret="fail"

  # perform db connectivity check for at least 60 times,
  # before give up
  while [[ $i -lt 61 ]]; do
    # Run hue dbshell, if successful then one should not see
    # psql in the output.
    dbshell_output=$(echo "\q"|$HUE_BIN/hue dbshell 2>&1)
    error_line=$(echo $dbshell_output|grep psql)
    if [[ $error_line -eq 0 ]]; then
      echo "Successful db connectivity check"
      ret="success"
      break
    fi

    i=$((i+1))
    # gradually increase sleep time
    sleep $i

    echo "Failing db connectivity error: " $i " " $dbshell_output
  done

  echo "$ret"
}

# If database connectivity is not set then fail
ret=$(db_connectivity_check)
if [[ $ret == "fail" ]];  then
  exit 1
fi

# prepare db schema, run it in single instance flock mode
prepare_huedb

if [[ $1 == kt_renewer ]]; then
  if [ -e "/etc/hue/conf/kerberos.ini" ]; then
    # The Kerberos ticket renewer role needs to know where kinit is.
    KINIT_PATH=`which kinit`
    KINIT_PATH=${KINIT_PATH-/usr/bin/kinit}
    $HUE_BIN/hue kt_renewer
  fi
elif [[ $1 == runcpserver ]]; then
    $HUE_BIN/hue runcherrypyserver
fi

exit 0
