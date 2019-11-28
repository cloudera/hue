#!/bin/sh
set -e
mkdir -p ${HUE_LOG_DIR}
rm -rf /run/httpd/* /tmp/httpd*

exec /usr/sbin/httpd -DFOREGROUND "$@"
