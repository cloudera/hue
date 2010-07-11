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

BINDIR=$(dirname $0)
desktop_root=$PWD

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

make apps

if python -V 2>&1 | grep -q -v 2.4; then
  # Install pylint from our archive
  build/env/bin/easy_install \
    -f http://archive.cloudera.com/desktop-sdk-python-packages/ \
    -H pypi.python.org,archive.cloudera.com pylint
  build/env/bin/desktop runpylint all -- -f parseable > PYLINT.txt
fi

rm -f JAVASCRIPTLINT.txt
for FILE in $(find . -name *.js);
do
  jsl -conf .jslintrc -nologo -nosummary -nocontext -nofilelisting -process $FILE >> JAVASCRIPTLINT.txt || /bin/true
done;

if [ "$1" == "slow" ]; then
  make test-slow
elif [ "$1" == "windmill" ]; then
  xvfb-run -a -s '-screen 0 1024x768x16' tools/scripts/hudson_windmill_in_X.sh
else
  make test docs
fi
