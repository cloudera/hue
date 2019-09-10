#!/bin/bash

set -ex

WORK_DIR=$(dirname $(readlink -f $0))
HUE_SRC=$(realpath $WORK_DIR/../..)
BUILD_DIR=$(realpath $HUE_SRC/../containerbuild$GBN)
HUE_DIR=$WORK_DIR/hue
APACHE_DIR=$WORK_DIR/huelb
REGISTRY=${REGISTRY:-"docker.io/hortonworks"}

compile_hue() {
  mkdir -p $BUILD_DIR
  cd $HUE_SRC
  PREFIX=$BUILD_DIR make install
  cd $BUILD_DIR/hue
  APPS=$(find apps -maxdepth 2 -name "src" -type d|cut -d"/" -f2|sort| sed 's/[^ ]* */apps\/&/g')
  ./build/env/bin/python tools/app_reg/app_reg.py --install $APPS --relative-paths
  bash tools/relocatable.sh
}

find_git_state() {
  cd $HUE_SRC
  export GBRANCH=$(git ls-remote  --get-url)"/commits/"$(git rev-parse --abbrev-ref HEAD)
  export GSHA=$(git ls-remote  --get-url)"/commit/"$(git rev-list --no-walk HEAD)
  export VERSION=$(grep "VERSION=" VERSION | cut -d"=" -f2 | cut -d'"' -f2)
}

generate_random_string() {
  cd $HUE_DIR
  thisuser=$(uuidgen | cut -d"-" -f5)
  thispass=$(uuidgen | cut -d"-" -f5)
  sed -i -e "s|6216803864979002924|${thisuser}|g" supervisor-files/etc/supervisord.conf
  sed -i -e "s|8373576301055810053|${thispass}|g" supervisor-files/etc/supervisord.conf
}

docker_hue_build() {
  cd $HUE_DIR
  generate_random_string
  cp -a $BUILD_DIR/hue $HUE_DIR
  rm -f $HUE_DIR/hue/desktop/conf/*
  docker build -f $HUE_DIR/Dockerfile -t ${REGISTRY}/hue:$GBN \
    --build-arg GBN=$GBN \
    --build-arg GSHA="$GSHA" \
    --build-arg GBRANCH=$GBRANCH \
    --build-arg VERSION=$VERSION \
    .
}

docker_huelb_build() {
  cd $APACHE_DIR
  cp -a $BUILD_DIR/hue/build/static $APACHE_DIR
  docker build -f $APACHE_DIR/Dockerfile -t ${REGISTRY}/huelb:$GBN \
    --build-arg GBN=$GBN \
    --build-arg GSHA="$GSHA" \
    --build-arg GBRANCH=$GBRANCH \
    --build-arg VERSION=$VERSION \
    .
}

compile_hue
find_git_state
docker_hue_build
docker_huelb_build
