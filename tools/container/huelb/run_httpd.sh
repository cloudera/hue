#!/bin/bash

set -e

exec /usr/sbin/httpd -D FOREGROUND -k start -C "ServerName $(hostname -i)"
