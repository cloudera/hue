#!/bin/bash

$HUE_BIN/hue syncdb --noinput
$HUE_BIN/hue migrate
$HUE_BIN/hue runserver 0.0.0.0:8888
