#!/bin/sh

export HUE_LOG_DIR="/var/log/hue"
mkdir -p ${HUE_LOG_DIR}

set -e

# Apache gets grumpy about PID files pre-existing
rm -f /usr/local/apache2/logs/httpd.pid

exec httpd -DFOREGROUND "$@"
