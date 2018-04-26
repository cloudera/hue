#!/usr/bin/env bash

set -e -x

docker pull $DOCKER_IMAGE

docker run --rm -v `pwd`:/io $DOCKER_IMAGE $PRE_CMD /io/.manylinux-install.sh

pip install twine && twine upload -u zope.wheelbuilder -p $PYPIPASSWORD wheelhouse/*
