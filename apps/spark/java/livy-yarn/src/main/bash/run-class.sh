#!/bin/bash

home_dir=`pwd`
base_dir=$(dirname $0)/..
cd $base_dir
base_dir=`pwd`
cd $home_dir

HADOOP_YARN_HOME="${HADOOP_YARN_HOME:-$HOME/.livy}"
HADOOP_CONF_DIR="${HADOOP_CONF_DIR:-$HADOOP_YARN_HOME/conf}"
CLASSPATH="$HADOOP_CONF_DIR:$base_dir/lib/*"
DEFAULT_LOGBACK_FILE="$base_dir/resources/logback.xml"

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

# Check if logback configuration is specified. If not - set to resources/logback.xml
[[ $JAVA_OPTS != *-Dlogback.configuration* && -f $DEFAULT_LOGBACK_FILE ]] && JAVA_OPTS="$JAVA_OPTS -Dlogback.configuration=file:$DEFAULT_LOGBACK_FILE"

echo $JAVA $JAVA_OPTS -cp "$CLASSPATH" "$@"
exec $JAVA $JAVA_OPTS -cp "$CLASSPATH" "$@"
