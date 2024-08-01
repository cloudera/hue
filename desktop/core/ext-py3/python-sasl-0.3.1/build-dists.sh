#!/bin/bash
# Copyright 2015 Cloudera Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -x

# Usage info
show_help() {
cat << EOF
Usage: ${0##*/} [-h] [-a GITHUB_ACCOUNT] GIT_VERSION_TAG
  -h                 display this help and exit
  -a GITHUB_ACCOUNT  use GITHUB_ACCOUNT instead of 'cloudera'
EOF
}

# Parse command line options
GITHUB_ACCOUNT="cloudera"
GIT_VERSION_TAG=""

OPTIND=1
while getopts ha: opt; do
    case $opt in
        h)
            show_help
            exit 0
            ;;
        a)  GITHUB_ACCOUNT=$OPTARG
            ;;
        *)
            show_help >&2
            exit 1
            ;;
    esac
done
shift "$((OPTIND-1))"   # Discard the options and sentinel --

GIT_VERSION_TAG="$1"
if [ -z "$GIT_VERSION_TAG" ] || [ "$#" -gt 1 ]; then
  show_help >&2
  exit 1
fi

# Start build script in manylinux docker container
DOCKER_IMAGE='quay.io/pypa/manylinux1_x86_64'

docker pull "$DOCKER_IMAGE"
docker container run -t --rm  -v "$(pwd)/io:/io" "$DOCKER_IMAGE" \
  "/io/manylinux/build.sh" \
    "/io/pip-dists-build" \
    "$GIT_VERSION_TAG" \
    "$GITHUB_ACCOUNT"

RETVAL="$?"
if [[ "$RETVAL" != "0" ]]; then
	echo "Failed with $RETVAL"
else
	echo "Succeeded"
fi
exit $RETVAL
