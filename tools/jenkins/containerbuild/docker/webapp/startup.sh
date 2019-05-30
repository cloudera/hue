#!/bin/sh

/opt/hue/build/env/bin/hue syncdb --noinput
/opt/hue/build/env/bin/hue migrate
/opt/hue/build/env/bin/hue runserver 0.0.0.0:8888
