#!/usr/bin/env bash

ALIAS=$1
if [ "${ALIAS}" = "" ]; then
    echo "Alias not provided" >&2
    exit 1
fi

JCEKS_PATH=$2
if [ "${JCEKS_PATH}" = "" ]; then
    JCEKS_PATH="/jceks/secrets.jceks"
fi

exec ${JAVA_HOME}/bin/java -cp /etc/hue/conf/security-7.2.3.jar com.cloudera.enterprise.crypto.JceksPasswordExtractor "${JCEKS_PATH}" "${ALIAS}"
