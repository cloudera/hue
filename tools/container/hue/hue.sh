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

function set_samlcert() {
  mkdir -pm 755 $HUE_CONF_DIR/samlcert
  cd $HUE_CONF_DIR/samlcert
  export RANDFILE=$HUE_CONF_DIR/samlcert/.rnd
  if [ -z ${PASSPHRASE+x} ]; then
    openssl genrsa -des3 -passout pass:cloudera -out server.pass.key 2048
    openssl rsa -inform PEM -outform PEM -passin pass:cloudera -in server.pass.key -out server.key
    openssl req -new -key server.key -out server.csr -subj "/C=US/ST=California/L=Palo Alto/O=Cloudera/OU=Hue/CN=$EXTERNAL_HOST"
    openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
  else
    echo "#!/bin/bash" > $HUE_CONF_DIR/samlcert/pass.key
    echo "echo \$PASSPHRASE" >> $HUE_CONF_DIR/samlcert/pass.key
    chmod a+x $HUE_CONF_DIR/samlcert/pass.key
    openssl genrsa -des3 -passout pass:$PASSPHRASE -out server.key 2048
    openssl req -new -key server.key -out server.csr -passin pass:$PASSPHRASE -subj "/C=US/ST=California/L=Palo Alto/O=Cloudera/OU=Hue/CN=$EXTERNAL_HOST"
    openssl x509 -req -days 365 -in server.csr -passin pass:$PASSPHRASE -signkey server.key -out server.crt
  fi
  export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib64
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
  if [ -e "/etc/hue/conf/saml.ini" ]; then
    set_samlcert
  fi
  $HUE_BIN/hue runcherrypyserver
fi

exit 0
