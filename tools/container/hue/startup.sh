#!/bin/bash

export DESKTOP_LOG_DIR="/var/log/hue"
export PYTHON_EGG_CACHE=$HUE_CONF_DIR/.python-eggs
export SERVER_SOFTWARE="apache"

$HUE_BIN/hue syncdb --noinput
$HUE_BIN/hue migrate
$HUE_BIN/hue runcherrypyserver
