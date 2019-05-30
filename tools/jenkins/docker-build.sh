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
#DOCKER_REGISTRY=${DOCKER_REGISTRY:-"docker-registry.infra.cloudera.com/huecontainer"}
docker login --username=$DOCKER_USERNAME --password=$DOCKER_PASSWORD docker.io
DOCKER_REGISTRY=${DOCKER_REGISTRY:-"docker.io/ranade2005"}
BASEDOCKER=${DOCKER_REGISTRY}/${BASEIMAGE}

build_base() {
  BASE_DIR=$BUILD_DIR/docker/base
  cd $BUILD_DIR

  docker build -f $BASE_DIR/Dockerfile -t $BASEDOCKER . 1>$DOCKER_LOG 2>&1
  docker tag $BASEDOCKER $BASEIMAGE 1>$DOCKER_LOG 2>&1
  docker tag $BASEDOCKER $BASEOS:latest 1>$DOCKER_LOG 2>&1
  docker tag $BASEDOCKER $DOCKER_REGISTRY/$BASEOS:latest 1>$DOCKER_LOG 2>&1
  docker push $BASEDOCKER 1>$DOCKER_LOG 2>&1
}

pull_base() {
  BASE_DIR=$BUILD_DIR/docker/base
  cd $BUILD_DIR

  docker pull $BASEDOCKER 1>$DOCKER_LOG 2>&1
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
  WEBAPPIMAGE="huewebapp:$GBN"
  LATESTWEBAPPIMAGE="huewebapp:latest"

  cd $BUILD_DIR
  docker build -f $WEBAPP_DIR/Dockerfile -t $WEBAPPIMAGE . 1>$DOCKER_LOG 2>&1
  docker tag $WEBAPPIMAGE $DOCKER_USERNAME/$WEBAPPIMAGE  1>$DOCKER_LOG 2>&1
  docker tag $WEBAPPIMAGE $DOCKER_REGISTRY/$WEBAPPIMAGE  1>$DOCKER_LOG 2>&1
  docker tag $DOCKER_REGISTRY/$WEBAPPIMAGE $DOCKER_REGISTRY/$LATESTWEBAPPIMAGE 1>$DOCKER_LOG 2>&1
}

push_webapp() {
  WEBAPPIMAGE="huewebapp:$GBN"
  cd $BUILD_DIR
  docker push $DOCKER_REGISTRY/$WEBAPPIMAGE 1>$DOCKER_LOG 2>&1
}

build_httpd() {
  HTTPD_DIR=$BUILD_DIR/docker/httpd
  HTTPDIMAGE="huehttpd:$GBN"
  LATESTHTTPDIMAGE="huehttpd:latest"

  cd $BUILD_DIR

  docker build -f $HTTPD_DIR/Dockerfile -t $HTTPDIMAGE . 1>$DOCKER_LOG 2>&1
  docker tag $HTTPDIMAGE $DOCKER_USERNAME/$HTTPDIMAGE 1>$DOCKER_LOG 2>&1
  docker tag $HTTPDIMAGE $DOCKER_REGISTRY/$HTTPDIMAGE 1>$DOCKER_LOG 2>&1
  docker tag $DOCKER_REGISTRY/$HTTPDIMAGE $DOCKER_REGISTRY/$LATESTHTTPDIMAGE 1>$DOCKER_LOG 2>&1
}

push_httpd() {
  HTTPDIMAGE="huehttpd:$GBN"

  cd $BUILD_DIR

  docker push $DOCKER_REGISTRY/$HTTPDIMAGE 1>$DOCKER_LOG 2>&1
}

build_huedb() {
  HUEDB_DIR=$BUILD_DIR/docker/huedb
  HUEDBIMAGE="huedb:$GBN"
  LATESTHUEDBIMAGE="huedb:latest"

  cd $BUILD_DIR

  docker build -f $HUEDB_DIR/Dockerfile -t $HUEDBIMAGE . 1>$DOCKER_LOG 2>&1
  docker tag $HUEDBIMAGE $DOCKER_USERNAME/$HUEDBIMAGE 1>$DOCKER_LOG 2>&1
  docker tag $HUEDBIMAGE $DOCKER_REGISTRY/$HUEDBIMAGE 1>$DOCKER_LOG 2>&1
  docker tag $DOCKER_REGISTRY/$HUEDBIMAGE $DOCKER_REGISTRY/$LATESTHUEDBIMAGE 1>$DOCKER_LOG 2>&1
}

push_huedb() {
  HUEDBIMAGE="huedb:$GBN"

  cd $BUILD_DIR

  docker push $DOCKER_REGISTRY/$HUEDBIMAGE 1>$DOCKER_LOG 2>&1
}

build_base

pull_base
compile_webapp
build_webapp
push_webapp

build_httpd
push_httpd

build_huedb
push_huedb
#build_taskserver
#push_taskserver
