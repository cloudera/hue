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
# Runs Livy server.

set -o errexit

LIVY_ROOT=$(dirname $0)
LIVY_JAR=$LIVY_ROOT/java/livy-server/target/livy-server-3.7.0-SNAPSHOT.jar

export LIVY_HOME=$(dirname $0)

# Note: I've had trouble running this with just "java -jar" with the classpath
# determined with a seemingly appropriate find command.
echo CWD=$(pwd)
echo Executing java -jar $LIVY_JAR "$@"
exec java -jar $LIVY_JAR "$@"
