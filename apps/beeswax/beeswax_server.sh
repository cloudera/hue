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
# Runs Beeswax server.

set -o errexit

if [ -z "$HADOOP_HOME" ]; then
  echo "\$HADOOP_HOME must be specified" 1>&2
  exit 1
fi

if [ -z "$HIVE_CONF_DIR" ]; then
  echo "\$HIVE_CONF_DIR must be specified" 1>&2
  exit 1
fi


BEESWAX_ROOT=$(dirname $0)
BEESWAX_JAR=$BEESWAX_ROOT/java-lib/BeeswaxServer.jar
BEESWAX_HIVE_LIB=$BEESWAX_ROOT/hive/lib

echo \$HADOOP_HOME=$HADOOP_HOME

export HADOOP_CLASSPATH=$(find $BEESWAX_HIVE_LIB -name "*.jar" | tr "\n" :):$HIVE_CONF_DIR:$BEESWAX_ROOT/../../desktop/libs/hadoop/static-group-mapping/java-lib/static-group-mapping-1.1.0.jar
export HADOOP_OPTS="-Dlog4j.configuration=log4j.properties"
echo \$HADOOP_CLASSPATH=$HADOOP_CLASSPATH
echo \$HADOOP_OPTS=$HADOOP_OPTS

# Use HADOOP_CONF_DIR to preprend to classpath, to avoid fb303 conflict,
# and to force hive-default to correspond to the Hive version we have.
# Because we are abusing HADOOP_CONF_DIR, we have to emulate its default
# behavior here as well.
if [ -z "$HADOOP_CONF_DIR" ]; then
  HADOOP_CONF_DIR="$HADOOP_HOME/conf"
fi
if [ -f $HADOOP_CONF_DIR/hadoop-env.sh ]; then
  . $HADOOP_CONF_DIR/hadoop-env.sh
fi
export HADOOP_CONF_DIR=$BEESWAX_ROOT/../../desktop/conf:${BEESWAX_HIVE_LIB}/hive-default-xml-0.5.0.jar:${HADOOP_CONF_DIR}:$(find $BEESWAX_HIVE_LIB -name "libfb303.jar" | head -1)
echo \$HADOOP_CONF_DIR=$HADOOP_CONF_DIR

# Note: I've had trouble running this with just "java -jar" with the classpath
# determined with a seemingly appropriate find command.
echo Executing $HADOOP_HOME/bin/hadoop jar $BEESWAX_JAR "$@"
exec $HADOOP_HOME/bin/hadoop jar $BEESWAX_JAR "$@"
