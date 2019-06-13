#!/bin/sh

./build/env/bin/hue syncdb --noinput
./build/env/bin/hue migrate
./build/env/bin/supervisor
