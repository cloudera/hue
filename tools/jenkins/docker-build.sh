#!/bin/bash

set -e
set -x

BINDIR=$(dirname $(readlink -f $0))
ROOT=${BINDIR%/*/*/*}
DOCKER_LOG=/var/log/hue-docker.log

GBN=$(curl http://gbn.infra.cloudera.com/)

BUILD_DIR=$BINDIR/containerbuild

# docker build -f httpd/Dockerfile -t httpdnew:2 .
BASEOS="ubuntu1804"
BASEIMAGE="${BASEOS}:base"
DOCKER_REGISTRY=${DOCKER_REGISTRY:-"docker-registry.infra.cloudera.com/huecontainer"}
BASEDOCKER=${DOCKER_REGISTRY}/${BASEIMAGE}

build_base() {
  BASE_DIR=$BUILD_DIR/docker/base
  cd $BUILD_DIR

  docker build -f $BASE_DIR/Dockerfile -t $BASEDOCKER . 1>$DOCKER_LOG 2>&1
  docker tag $BASEDOCKER $BASEIMAGE 1>$DOCKER_LOG 2>&1
  docker tag $BASEDOCKER $BASEOS:latest 1>$DOCKER_LOG 2>&1
  docker push $BASEDOCKER 1>$DOCKER_LOG 2>&1
}

compile_webapp() {
  LOCAL_SRC=$ROOT/hue
  DOCKER_DST=/hue
  DEPLOY_DIR=/opt
  BUILD_LOG=$BUILD_DIR/hue-build.log

  cd $BUILD_DIR

  docker run -it -v $LOCAL_SRC:$DOCKER_DST -v $BUILD_DIR:$DEPLOY_DIR $BASEDOCKER bash -c "cd /hue; PREFIX=/opt make install" 1>$BUILD_LOG 2>&1
  docker run -it -v $LOCAL_SRC:$DOCKER_DST -v $BUILD_DIR:$DEPLOY_DIR $BASEDOCKER bash -c "cd /opt; /opt/hue/build/env/bin/hue collectstatic --noinput" 1>$BUILD_LOG 2>&1
  docker run -it -v $LOCAL_SRC:$DOCKER_DST -v $BUILD_DIR:$DEPLOY_DIR $BASEDOCKER bash -c "cd /opt; /opt/hue/build/env/bin/pip install psycopg2-binary" 1>$BUILD_LOG 2>&1
}

build_webapp() {
  WEBAPP_DIR=$BUILD_DIR/docker/webapp
  WEBAPPIMAGE="webapp:$GBN"

  cd $BUILD_DIR
  docker build -f $WEBAPP_DIR/Dockerfile -t $WEBAPPIMAGE . 1>$DOCKER_LOG 2>&1
  docker tag $WEBAPPIMAGE $DOCKER_REGISTRY/$WEBAPPIMAGE  1>$DOCKER_LOG 2>&1
}

push_webapp() {
  WEBAPPIMAGE="webapp:$GBN"
  cd $BUILD_DIR
  docker push $DOCKER_REGISTRY/$WEBAPPIMAGE 1>$DOCKER_LOG 2>&1
}

build_httpd() {
  HTTPD_DIR=$BUILD_DIR/docker/httpd
  HTTPDIMAGE="httpd:$GBN"

  cd $BUILD_DIR

  docker build -f $HTTPD_DIR/Dockerfile -t $HTTPDIMAGE . 1>$DOCKER_LOG 2>&1
  docker tag $HTTPDIMAGE $DOCKER_REGISTRY/$HTTPDIMAGE 1>$DOCKER_LOG 2>&1
}

push_httpd() {
  HTTPDIMAGE="httpd:$GBN"

  cd $BUILD_DIR

  docker push $DOCKER_REGISTRY/$HTTPDIMAGE 1>$DOCKER_LOG 2>&1
}

build_base
compile_webapp
build_webapp
push_webapp

build_httpd
push_httpd

#build_taskserver
#push_taskserver
