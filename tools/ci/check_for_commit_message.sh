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

FOUND_ISSUE=0
IFS=$'\n'

for commit in `git log origin/master..master --format="%s"`
do
 ./tools/githooks/commit-msg "" "$commit"

 if [ "$?" -ne "0" ]
  then
    echo "Not matching commit title '$commit'"
    FOUND_ISSUE=-1
  fi
done

if [ "$FOUND_ISSUE" -eq "0" ]
then
  echo "All commit titles are good"
fi

unset IFS

exit $FOUND_ISSUE
