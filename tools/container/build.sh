#!/bin/bash

set -ex

# Time marker for both stderr and stdout
date; date 1>&2

WORK_DIR=$(dirname $(readlink -f $0))
. ${WORK_DIR}/common.sh

HUE_SRC=$(realpath $WORK_DIR/../..)
BUILD_DIR=$(realpath $HUE_SRC/../containerbuild$GBN)

HUE_DIR=$WORK_DIR/hue
APACHE_DIR=$WORK_DIR/huelb
BASEHUE_DIR=$WORK_DIR/base/hue
BASEHUELB_DIR=$WORK_DIR/base/huelb
COMPILEHUE_DIR=$WORK_DIR/compile/hue

COMPILEHUE_VERSION=huecompile_ubi:$DOCKERHUEBASE_VERSION
HUEBASE_VERSION=huebase_ubi:$DOCKERHUEBASE_VERSION
HUELBBASE_VERSION=huelb_httpd_ubi:$DOCKERHUELB_VERSION

CONTAINER_HUE_SRC=/root/${HUEUSER}
CONTAINER_HUE_OPT=/opt

# This step is performed inside the docker(compile step)
compile_py3hue() {
  export HUE_HOME="/opt/${HUEUSER}"
  export ROOT="/opt/${HUEUSER}"
  mkdir -p $CONTAINER_HUE_OPT
  cd $CONTAINER_HUE_SRC
  INSTALL_DIR=${HUE_HOME} make install
  cd $CONTAINER_HUE_OPT/${HUEUSER}
  APPS=$(find apps -maxdepth 2 -name "src" -type d|cut -d"/" -f2|sort| sed 's/[^ ]* */apps\/&/g')
  ./build/env/bin/python tools/app_reg/app_reg.py --install $APPS --relative-paths
}

# Compile the bits in the docker and copy it out
docker_hue_compile() {
  export HUE_CONF="/etc/hue"
  export HUE_HOME="/opt/${HUEUSER}"
  export HUE_CONF_DIR="${HUE_CONF}/conf"
  export HUE_LOG_DIR="/var/log/${HUEUSER}"
  export CONTAINER=$(uuidgen | cut -d"-" -f5)

  mkdir -p $BUILD_DIR
  docker run -dt --name $CONTAINER $COMPILEHUE_VERSION /bin/bash
  docker container cp $HUE_SRC $CONTAINER:$CONTAINER_HUE_SRC
  docker container exec $CONTAINER $CONTAINER_HUE_SRC/tools/container/build.sh compile_py3hue
  docker container cp $CONTAINER:$CONTAINER_HUE_OPT/${HUEUSER} $BUILD_DIR
  docker container stop $CONTAINER
}

docker_hue_build() {
  export HUE_CONF="/etc/hue"
  export HUE_HOME="/opt/${HUEUSER}"
  export HUE_CONF_DIR="${HUE_CONF}/conf"
  export HUE_LOG_DIR="/var/log/${HUEUSER}"
  export UUID_GEN=$(uuidgen | cut -d"-" -f5)

  cd $HUE_DIR
  cp -a $BUILD_DIR/${HUEUSER} $HUE_DIR
  rm -f $HUE_DIR/${HUEUSER}/desktop/conf/*

  # Remove chardet package
  rm -rf $HUE_DIR/${HUEUSER}/tools/virtual-bootstrap/virtualenv_support

  # Reduce Hue container size
  rm -rf $HUE_DIR/${HUEUSER}/node_modules
  rm -rf $HUE_DIR/${HUEUSER}/desktop/core/ext-eggs

  for f in $(find $HUE_DIR/supervisor-files -name "*_template"); do
    subst_var $f
  done

  sed -i -e "s#\${HUEBASE_VERSION}#${HUEBASE_VERSION}#g" $HUE_DIR/Dockerfile
  docker build -f $HUE_DIR/Dockerfile -t ${REGISTRY}/hue:$GBN \
    --build-arg GBN=$GBN \
    --build-arg GSHA="$GSHA" \
    --build-arg GBRANCH=$GBRANCH \
    --build-arg VERSION=$VERSION \
    --build-arg HUEUSER=$HUEUSER \
    --build-arg HUE_CONF=$HUE_CONF \
    .
}

docker_huelb_build() {
  export HUE_CONF="/etc/hue"
  export HUE_HOME="/opt/${HUEUSER}"
  export HUE_CONF_DIR="${HUE_CONF}/conf"
  export HUE_LOG_DIR="/var/log/${HUEUSER}"

  cd $APACHE_DIR
  cp -a $BUILD_DIR/${HUEUSER}/build/static $APACHE_DIR

  for f in $(find $APACHE_DIR -name "*_template"); do
    subst_var $f
  done

  sed -i -e "s#\${HUELBBASE_VERSION}#${HUELBBASE_VERSION}#g" $APACHE_DIR/Dockerfile
  docker build -f $APACHE_DIR/Dockerfile -t ${REGISTRY}/huelb:$GBN \
    --build-arg GBN=$GBN \
    --build-arg GSHA="$GSHA" \
    --build-arg GBRANCH=$GBRANCH \
    --build-arg VERSION=$VERSION \
    --build-arg HUEUSER=$HUEUSER \
    --build-arg HUE_CONF=$HUE_CONF \
    .
}

build_huebase() {
  cd $BASEHUE_DIR
  docker build -f $BASEHUE_DIR/Dockerfile -t ${REGISTRY}/$HUEBASE_VERSION .
  docker tag ${REGISTRY}/$HUEBASE_VERSION $HUEBASE_VERSION
  docker push ${REGISTRY}/$HUEBASE_VERSION
  docker pull ${REGISTRY}/$HUEBASE_VERSION
}

build_huelbbase() {
  cd $BASEHUELB_DIR
  docker build -f $BASEHUELB_DIR/Dockerfile -t ${REGISTRY}/$HUELBBASE_VERSION .
  docker tag ${REGISTRY}/$HUELBBASE_VERSION $HUELBBASE_VERSION
  docker push ${REGISTRY}/$HUELBBASE_VERSION
  docker pull ${REGISTRY}/$HUELBBASE_VERSION
}

build_huecompilebase() {
  cd $COMPILEHUE_DIR
  docker build -f $COMPILEHUE_DIR/Dockerfile -t ${REGISTRY}/$COMPILEHUE_VERSION .
  docker tag ${REGISTRY}/$COMPILEHUE_VERSION $COMPILEHUE_VERSION
  docker push ${REGISTRY}/$COMPILEHUE_VERSION
  docker pull ${REGISTRY}/$COMPILEHUE_VERSION
}

pull_base_images() {
  docker pull ${REGISTRY}/$HUEBASE_VERSION
  if [[ $? -ne 0 ]]; then
    build_huebase
  fi
  docker tag ${REGISTRY}/$HUEBASE_VERSION $HUEBASE_VERSION

  docker pull ${REGISTRY}/$HUELBBASE_VERSION
  if [[ $? -ne 0 ]]; then
    build_huelbbase
  fi
  docker tag ${REGISTRY}/$HUELBBASE_VERSION $HUELBBASE_VERSION

  docker pull ${REGISTRY}/$COMPILEHUE_VERSION
  if [[ $? -ne 0 ]]; then
    build_huecompilebase
  fi
  docker tag ${REGISTRY}/$COMPILEHUE_VERSION $COMPILEHUE_VERSION
}

rebuild_base_images() {
  docker pull registry.access.redhat.com/ubi8/ubi:latest
  build_huebase
  build_huelbbase
  build_huecompilebase
}

hue_containers_build() {
  if [ $REBUILD_BASE -gt 0 ]; then
    rebuild_base_images
  fi
  pull_base_images
  find_git_state

  # compile hue code in compile container
  docker_hue_compile

  # package compiled hue code in runtime container
  docker_hue_build
  docker_huelb_build
}

wait_for_parallel_jobs() {
  EXIT=0
  jobs -l
  for job in `jobs -p`; do
    echo $job
    wait $job || let "EXIT+=1"
  done

  if [[ "$EXIT" == "0" ]]; then
    exit 0
  else
    exit 1
  fi
}

if [[ $1 == "compile_py3hue" ]]; then
  compile_py3hue
else
  # Perform Hue Code Compilation and Docker packaging
  hue_containers_build

  # Perform any other container build process
  extra_container_build=$(find_extra_container_to_build)
  if test -n "$extra_container_build"; then
    $extra_container_build
  fi

  # Wait for the parallel jobs to finish
  wait_for_parallel_jobs
fi
