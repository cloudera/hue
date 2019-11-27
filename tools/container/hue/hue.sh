#!/bin/bash
# Copyright (c) 2019 Cloudera, Inc. All rights reserved.

set -x

# Time marker for both stderr and stdout
date; date 1>&2

export DESKTOP_LOG_DIR="/var/log/hive"
export PYTHON_EGG_CACHE=$HUE_CONF_DIR/.python-eggs
export SERVER_SOFTWARE="apache"

function prepare_huedb() {
  $HUE_BIN/hue syncdb --noinput
  $HUE_BIN/hue makemigrations --noinput --merge
  $HUE_BIN/hue migrate
}

function db_connectivity_check() {
  i="0"
  ret="fail"

  # perform db connectivity check for 5 times
  while [[ $i -lt 5 ]]; do
    echo "Running db connectivity check"

    status=$(echo quit|$HUE_BIN/hue dbshell 2>&1|wc -l)
    # check if db connection is successful
    if [[ $status -gt 1 ]]; then
      ret="success"
      break
    fi

    sleep 1
    i=$[$i+1]

    echo "Failing db connectivity check: $i"
  done

  echo "$ret"
}

# If database connectivity is not set then fail
ret=$(db_connectivity_check)
if [[ $ret == "fail" ]];  then
  exit 1
fi

# prepare db schema
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
