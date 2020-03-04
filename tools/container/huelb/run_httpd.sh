#!/bin/sh
set -e
mkdir -p ${HUE_LOG_DIR}
ip_address=$(hostname -i)

exec /usr/sbin/httpd -DFOREGROUND "$@"
