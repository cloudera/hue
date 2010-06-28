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
#
# Checks that the tarball at the given path can install without network access
set -e
if [ $# != 1 -o ! -f $1 ]; then
  echo usage: $0 path/to/hue.tgz
  exit 1
fi

TMP=$(mktemp -d)

cleanup() {
  rm -Rf $TMP
}
trap cleanup EXIT

echo "Unpacking tarball in $TMP..."
cat $1 | (cd $TMP && tar xzf -)
echo "Done"

cd $TMP
cd hue*
PREFIX=$TMP/install-prefix \
  strace -f "-o|tee $TMP/install-trace" -econnect -e signal= \
  make install

echo Checking for network accesses...
if grep sa_family=AF_INET $TMP/install-trace ; then
  echo make install talked to the network!
  exit 1
fi

echo No network access detected. Hooray!
