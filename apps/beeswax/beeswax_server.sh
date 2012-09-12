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

if [ -z "$HADOOP_CONF_DIR" ]; then
  echo "\$HADOOP_CONF_DIR must be specified" 1>&2
  exit 1
fi
echo \$HADOOP_HOME=$HADOOP_HOME

if [ -z "$HADOOP_BIN" ]; then
  echo "\$HADOOP_BIN must be specified" 1>&2
  exit 1
fi
echo \$HADOOP_BIN=$HADOOP_BIN

if [ -z "$HIVE_CONF_DIR" ]; then
  echo "\$HIVE_CONF_DIR must be specified" 1>&2
  exit 1
fi

echo \$HIVE_CONF_DIR=$HIVE_CONF_DIR

if [ -z "$HIVE_HOME" ]; then
  echo "\$HIVE_HOME not specified. Defaulting to $HIVE_CONF_DIR/.." 1>&2
  export HIVE_HOME=$HIVE_CONF_DIR/..
  exit 1
fi

echo \$HIVE_HOME=$HIVE_HOME

BEESWAX_ROOT=$(dirname $0)
BEESWAX_JAR=$BEESWAX_ROOT/java-lib/BeeswaxServer.jar
HIVE_LIB=$HIVE_HOME/lib

export HADOOP_CLASSPATH=$(find $HADOOP_HOME -name hue-plugins*.jar | tr "\n" :):$(find $HIVE_LIB -name "*.jar" | tr "\n" :)

if [ -n "$HADOOP_EXTRA_CLASSPATH_STRING" ]; then
  export HADOOP_CLASSPATH=$HADOOP_CLASSPATH:$HADOOP_EXTRA_CLASSPATH_STRING
fi

export HADOOP_OPTS="-Dlog4j.configuration=log4j.properties"
echo \$HADOOP_CLASSPATH=$HADOOP_CLASSPATH
echo \$HADOOP_OPTS=$HADOOP_OPTS

# Use HADOOP_CONF_DIR to preprend to classpath, to avoid fb303 conflict,
# and to force hive-default to correspond to the Hive version we have.
# Because we are abusing HADOOP_CONF_DIR, we have to emulate its default
# behavior here as well.
if [ -f $HADOOP_CONF_DIR/hadoop-env.sh ]; then
  . $HADOOP_CONF_DIR/hadoop-env.sh
fi

export HADOOP_CONF_DIR=$HIVE_CONF_DIR:$HADOOP_CONF_DIR
echo \$HADOOP_CONF_DIR=$HADOOP_CONF_DIR
echo \$HADOOP_MAPRED_HOME=$HADOOP_MAPRED_HOME

# Note: I've had trouble running this with just "java -jar" with the classpath
# determined with a seemingly appropriate find command.
echo CWD=$(pwd)
echo Executing $HADOOP_BIN jar $BEESWAX_JAR "$@"
exec $HADOOP_BIN jar $BEESWAX_JAR "$@"
