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

# arg is path to website root source directory
# e.g.
#   docs/docs-site
#   docs/gethue
#
# https://github.com/raviqqe/muffet
# go get -u github.com/raviqqe/muffet
#
# We lower the concurrency and whitelist Jiras to avoid hammering the external sites.


SOURCE=${1:-"docs/docs-site"}
LINT_EXIT_CODE=1

git diff --name-only origin/master --diff-filter=b | egrep "^$SOURCE"

if [ "$?" -eq "0" ];
  then
    cd $1
    echo $PATH

    hugo serve&
    HUGO_PID=$!

    sleep 5

    muffet http://localhost:1313/ \
        --exclude "https://issues.cloudera.org*|http://localhost:5555*|https://issues.apache.org/jira*|https://github.com*|http://demo.gethue.com*" \
        --ignore-fragments \
        --timeout 15 \
        --concurrency 10
    LINT_EXIT_CODE=$?

    kill $HUGO_PID
  else
    echo "No documentation change"
    LINT_EXIT_CODE=0
fi

exit $LINT_EXIT_CODE
