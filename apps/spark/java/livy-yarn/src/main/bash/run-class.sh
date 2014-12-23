#!/bin/bash

home_dir=`pwd`
base_dir=$(dirname $0)/..
cd $base_dir
base_dir=`pwd`
cd $home_dir

HADOOP_YARN_HOME="${HADOOP_YARN_HOME:-$HOME/.livy}"
HADOOP_CONF_DIR="${HADOOP_CONF_DIR:-$HADOOP_YARN_HOME/conf}"
CLASSPATH="$HADOOP_CONF_DIR:$base_dir/lib/*"
DEFAULT_LOG4J_FILE="$base_dir/resources/log4j.properties"

#for file in $base_dir/lib/*.[jw]ar;
#do
#  CLASSPATH=$CLASSPATH:$file
#done

if [ -z "$JAVA_HOME" ]; then
  JAVA="java"
else
  JAVA="$JAVA_HOME/bin/java"
fi

# Try and use 64-bit mode if available in JVM_OPTS
function check_and_enable_64_bit_mode {
  `$JAVA -d64 -version`
  if [ $? -eq 0 ] ; then
    JAVA_OPTS="$JAVA_OPTS -d64"
  fi
}

# Check if 64 bit is set. If not - try and set it if it's supported
[[ $JAVA_OPTS != *-d64* ]] && check_and_enable_64_bit_mode

# Check if log4j configuration is specified. If not - set to lib/log4j.xml
[[ $JAVA_OPTS != *-Dlog4j.configuration* && -f $DEFAULT_LOG4J_FILE ]] && JAVA_OPTS="$JAVA_OPTS -Dlog4j.configuration=file:$DEFAULT_LOG4J_FILE"

JAVA_OPTS="$JAVA_OPTS -agentlib:jdwp=transport=dt_socket,server=y,suspend=y,address=5006"

echo $JAVA $JAVA_OPTS -cp "$CLASSPATH" "$@"
exec $JAVA $JAVA_OPTS -cp "$CLASSPATH" "$@"
