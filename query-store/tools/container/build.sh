#!/bin/bash

set -ex

# Time marker for both stderr and stdout
date; date 1>&2

WORK_DIR=$(dirname $(readlink -f $0))
. ${WORK_DIR}/../../../tools/container/common.sh

DOCKERHUEQP_VERSION=$DOCKERHUEBASE_VERSION

HUE_SRC=$(realpath $WORK_DIR/../../..)
BUILD_DIR=$(realpath $HUE_SRC/../containerbuild$GBN)
QPBUILD_DIR=$(realpath $HUE_SRC/../qpcontainerbuild$GBN)

QP_DIR=$WORK_DIR/queryprocessor
BASEHUEQP_DIR=$WORK_DIR/base/queryprocessor

HUEQPBASE_VERSION=hue_qp_ubi:$DOCKERHUEQP_VERSION

CONTAINER_HUE_SRC=/root/hue

# This step is performed inside the docker(compile step)
compile_qp() {
  cd $CONTAINER_HUE_SRC
  mvn -f query-store/pom.xml clean install
}

# Compile the bits in the docker and copy it out
docker_qp_compile() {
  export HUE_USER="hive"
  export HUE_CONF="/etc/hue"
  export HUE_HOME="/opt/${HUEUSER}"
  export HUE_CONF_DIR="${HUE_CONF}/conf"
  export HUE_LOG_DIR="/var/log/${HUEUSER}"
  export CONTAINER=$(uuidgen | cut -d"-" -f5)

  mkdir -p $QPBUILD_DIR
  docker run -dt --name $CONTAINER $HUEQPBASE_VERSION /bin/bash
  docker container cp $HUE_SRC $CONTAINER:$CONTAINER_HUE_SRC
  docker container exec $CONTAINER $CONTAINER_HUE_SRC/query-store/tools/container/build.sh compile_qp
  docker container cp $CONTAINER:$CONTAINER_HUE_SRC/query-store $QPBUILD_DIR/query-store
  docker container stop $CONTAINER
}


docker_qp_build() {
  export HUE_USER="hive"
  export HUE_CONF="/etc/hue"
  export HUE_HOME="/opt/${HUEUSER}"
  export HUE_CONF_DIR="${HUE_CONF}/conf"
  export HUE_LOG_DIR="/var/log/${HUEUSER}"
  export UUID_GEN=$(uuidgen | cut -d"-" -f5)

  mkdir -p $QP_DIR/target
  for tf in $(ls -1L $QPBUILD_DIR/query-store/query-processor/target/*tar.gz); do
    cd $QP_DIR/target
    tar zxvf $tf
  done
  cd $QP_DIR

  sed -i -e "s#\${HUEBASE_VERSION}#${HUEBASE_VERSION}#g" $QP_DIR/Dockerfile
  docker build -f $QP_DIR/Dockerfile -t ${REGISTRY}/hueqp:$GBN \
    --build-arg GBN=$GBN \
    --build-arg GSHA="$GSHA" \
    --build-arg GBRANCH=$GBRANCH \
    --build-arg VERSION=$VERSION \
    --build-arg HUEUSER=$HUEUSER \
    --build-arg HUE_CONF=$HUE_CONF \
    .
}

build_hueqpbase() {
  cd $BASEHUEQP_DIR
  docker build -f $BASEHUEQP_DIR/Dockerfile -t ${REGISTRY}/$HUEQPBASE_VERSION .
  docker tag ${REGISTRY}/$HUEQPBASE_VERSION $HUEQPBASE_VERSION
  docker push ${REGISTRY}/$HUEQPBASE_VERSION
  docker pull ${REGISTRY}/$HUEQPBASE_VERSION
}

pull_qpbase_images() {
  docker pull ${REGISTRY}/$HUEQPBASE_VERSION
  if [[ $? -ne  0 ]]; then
    build_hueqpbase
  fi
  docker tag ${REGISTRY}/$HUEQPBASE_VERSION $HUEQPBASE_VERSION
}

rebuild_qp_images() {
  docker pull registry.access.redhat.com/ubi7/ubi:latest
  build_hueqpbase
}

hue_qp_build() {
  if [ $REBUILD_BASE -gt 0 ]; then
    rebuild_qp_images
  fi
  pull_qpbase_images
  find_git_state

  docker_qp_compile
  docker_qp_build
}

if [[ $1 == "compile_qp" ]]; then
  compile_qp
else
  hue_qp_build
fi
