#!/bin/bash
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -e
set -x

# CDH3b3 requires tight umask setting.
umask 0022

BINDIR=$(dirname $0)
HUE_ROOT=$PWD

export REPO_TRACE=1

. $BINDIR/build-functions

# Use $SKIP_CLEAN if the cleaning is done outside of this script.
if [ -z "$SKIP_CLEAN" ]; then
  echo "Cleaning repo."
  git clean -xdf
  rm -rf ext
  git reset --hard HEAD
else
  echo "Skipping cleaning of repo."
fi

build_hadoop
build_hive
build_oozie
build_sqoop

make apps

build/env/bin/hue runpylint > PYLINT.txt

rm -f JAVASCRIPTLINT.txt
for FILE in $(find . -name *.js);
do
  jsl -conf .jslintrc -nologo -nosummary -nocontext -nofilelisting -process $FILE >> JAVASCRIPTLINT.txt || /bin/true
done;

if [ "$1" == "slow" ]; then
  make test-slow
elif [ "$1" == "windmill" ]; then
  xvfb-run -a -s '-screen 0 1024x768x16' tools/hudson/hudson_windmill_in_X.sh
else
  make test docs
fi
