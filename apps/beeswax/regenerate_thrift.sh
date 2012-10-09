#!/usr/bin/env bash
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

set -o errexit
set -o xtrace

cd $(dirname $0)

thrift -I thrift/include -r --gen py:new_style -o ./ thrift/beeswax.thrift
thrift -I thrift/include -r --gen java:hashcode -o java/src/main thrift/beeswax.thrift
thrift -I thrift/include -r --gen py:new_style -o ./ thrift/cli_service.thrift

# We don't need to have generated code for the metastore, since that's
# in one of the hive jars that we include
rm -Rf java/src/main/gen-java/com/facebook java/src/main/gen-java/org/apache

cat <<EOF
======================================================================
NOTE:
======================================================================

This script does *not* remove old generated files that may not be necessary anymore.
You should probably do something like:
 > git rm -rf java/src/main/gen-java gen-py
 > ./regenerate_thrift.sh
 > git add java/src/main/gen-java gen-py

======================================================================

EOF

# This is based on thirdparty.
# thrift -r --gen py:new_style -o ../ ../../../../ext/thirdparty/py/thrift/contrib/fb303/if/fb303.thrift
# C++ compilation for ODBC
#thrift -I thrift/include  --gen cpp -o ./ thrift/beeswax.thrift
