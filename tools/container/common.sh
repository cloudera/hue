#!/usr/bin/env bash

DOCKERHUEBASE_VERSION=8.5.7
DOCKERHUELB_VERSION=2.5.7
REBUILD_BASE=1

HUEUSER="hive"
CONTAINER=$(uuidgen | cut -d"-" -f5)

reset_git_state() {
  cd $HUE_SRC
  git clean -fdx
}

find_git_state() {
  cd $HUE_SRC
  export GBRANCH=$(git ls-remote  --get-url)"/commits/"$(git rev-parse --abbrev-ref HEAD)
  export GSHA=$(git ls-remote  --get-url)"/commit/"$(git rev-list --no-walk HEAD)
  export VERSION=$(grep "VERSION=" VERSION | cut -d"=" -f2 | cut -d'"' -f2)
  echo "GBRANCH=$GBRANCH" >> hue.version
  echo "GSHA=$GSHA" >> hue.version
  echo "VERSION=$VERSION" >> hue.version
  echo "GBN=$GBN" >> hue.version
}

find_extra_container_to_build() {
  cd $HUE_SRC
  workdir=""
  projects=$(find $HUE_SRC -path "*/tools/container/build.sh")
  skip_dir=$(dirname $(readlink -f build.sh))
  for proj in $(find $HUE_SRC -path "*/tools/container/build.sh"); do
    if [[ "$proj" != "$skip_dir/build.sh" ]] && [[ "$proj" != "$HUE_SRC/tools/container/build.sh" ]]; then
      workdir=${proj}
    fi
  done
  echo $workdir
}

subst_var() {
  file_name=$1
  if [[ -e $file_name ]]; then
    if [[ "$file_name" == *"_template" ]]; then
      out_name="${file_name::-9}.conf"
    fi
  fi

  eval "cat <<EOF
$(<$file_name)
EOF
" | tee $out_name 2> /dev/null
}

if [ -z "$REGISTRY" ]; then
  REGISTRY=${REGISTRY:-"docker.io/hortonworks"}
fi
