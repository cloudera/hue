#!/usr/bin/env bash

ALIAS=$1
if [ "${ALIAS}" = "" ]; then
    echo "Alias not provided" >&2
    exit 1
fi

exec /usr/bin/java -cp /etc/hue/conf/security-7.2.3.jar com.cloudera.enterprise.crypto.JceksPasswordExtractor /jceks/secrets.jceks "${ALIAS}"
