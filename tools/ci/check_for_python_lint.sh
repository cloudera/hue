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

# Checking all python changes in the new commits

FOUND_ISSUE=-1

files=`git diff --name-only origin/master --diff-filter=b | egrep .py$ | grep -v /ext-py/`

if [ ! -z "$files" ];
then
  ./build/env/bin/hue runpylint --files "$files"
fi

if [ -z "$files" ] || [ "$?" -eq "0" ]
then
  FOUND_ISSUE=0
  echo "No Python code styling issues found"
else
  echo "Found some Python code styling issues"
fi

exit $FOUND_ISSUE
