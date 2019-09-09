#!/bin/bash
# Copyright (c) 2019 Cloudera, Inc. All rights reserved.

set -x

# Time marker for both stderr and stdout
date; date 1>&2

export DESKTOP_LOG_DIR="/var/log/hue"
export PYTHON_EGG_CACHE=$HUE_CONF_DIR/.python-eggs
export SERVER_SOFTWARE="apache"

function prepare_hue_start() {
  $HUE_BIN/hue syncdb --noinput
  $HUE_BIN/hue migrate
}

if [[ $1 == kt_renewer ]]; then
  if [ -e "/etc/hue/conf/kerberos.ini" ]; then
    # The Kerberos ticket renewer role needs to know where kinit is.
    KINIT_PATH=`which kinit`
    KINIT_PATH=${KINIT_PATH-/usr/bin/kinit}
    $HUE_BIN/hue kt_renewer
  fi
elif [[ $1 == runcpserver ]]; then
    prepare_hue_start
    $HUE_BIN/hue runcherrypyserver
fi

exit 0
