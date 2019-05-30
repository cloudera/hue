#!/bin/bash

set -e
set -x

BINDIR=$(dirname $(readlink -f $0))
ROOT=${BINDIR%/*/*/*}
BUILD_LOG=/var/log/hue-build.log

BASEOS="ubuntu1604"
BASEIMAGE="${BASEOS}:base"
DOCKER_REGISTRY=${DOCKER_REGISTRY:-"docker-registry.infra.cloudera.com/huecontainer"}
BASEDOCKER=${DOCKER_REGISTRY}/${BASEIMAGE}

docker build -t $BASEDOCKER -f $BINDIR/Dockerfile . 1>$BUILD_LOG 2>&1
docker tag $BASEDOCKER $BASEIMAGE
docker tag $BASEDOCKER $BASEOS
docker push $BASEDOCKER 1>$BUILD_LOG 2>&1
