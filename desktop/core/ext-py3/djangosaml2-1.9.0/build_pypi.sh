#!/bin/bash

PROJ_NAME=$(ls | grep *.egg-info | sed -e 's/.egg-info//g') ; rm -R build/ dist/*  *.egg-info ; pip uninstall $PROJ_NAME ; python setup.py build sdist
twine upload dist/*
