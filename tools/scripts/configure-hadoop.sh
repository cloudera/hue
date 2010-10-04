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

set -o errexit

if test -z $HADOOP_HOME ; then
  echo "Please define your HADOOP_HOME environment variable."
  exit
fi

SCRIPT_DIR=$(dirname $0)
GIT_ROOT=$(cd $SCRIPT_DIR && pwd)/$(cd $SCRIPT_DIR && git rev-parse --show-cdup)
BIND_IP=${BIND_IP:-localhost}
HADOOP_TMP_DIR=$HADOOP_HOME/data

if [ $(uname) == "Darwin" ]; then
  export JAVA_HOME=/System/Library/Frameworks/JavaVM.framework/Versions/1.6.0/Home
fi
SLAVE_IPS=${SLAVE_IPS:-127.0.0.1}

echo -e ".======================== Parameters ========================\n"\
        "HADOOP_HOME    : $HADOOP_HOME\n"\
	"GIT_ROOT       : $GIT_ROOT\n"\
	"HADOOP_TMP_DIR : $HADOOP_TMP_DIR\n"\
	"============================================================\n"
set -x


# Configure a slave
# Used by the sandboxer
function write_hadoop_config() {
  SLAVE_IP=$1
  MASTER_IP=$2
  TARGET_DIR=$3
  TMP_DIR=$4
  if [ -z "$SLAVE_IP" -o -z "$MASTER_IP" -o -z "$TARGET_DIR" -o -z "$TMP_DIR" ]; then
    echo usage: $0 slave_ip master_ip target_conf_dir tmp_dir
    exit 1
  fi

  mkdir -p $TARGET_DIR
  cp $HADOOP_HOME/example-confs/conf.pseudo/hadoop-metrics.properties $TARGET_DIR
  cat > $TARGET_DIR/core-site.xml <<END
<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
<property>
  <name>fs.default.name</name>
  <value>hdfs://${MASTER_IP}:8020</value>
</property>
<property>
  <name>hadoop.tmp.dir</name>
  <value>$TMP_DIR</value>
  <description>A base for other temporary directories.</description>
</property>
<property>
  <name>webinterface.private.actions</name>
  <value>true</value>
</property>
<property>
  <name>slave.host.name</name>
  <value>${SLAVE_IP}</value>
</property>
<property>
  <name>dfs.thrift.address</name>
  <value>${MASTER_IP}:10090</value>
</property>
<property>
  <name>jobtracker.thrift.address</name>
  <value>${MASTER_IP}:9290</value>
</property>
</configuration>
END
  cat > $TARGET_DIR/hdfs-site.xml <<END
<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
<property>
  <name>dfs.datanode.address</name>
  <value>${SLAVE_IP}:0</value>
</property>
<property>
  <name>dfs.datanode.ipc.address</name>
  <value>${SLAVE_IP}:0</value>
</property>
<property>
  <name>dfs.datanode.http.address</name>
  <value>${SLAVE_IP}:0</value>
</property>
<property>
  <name>dfs.http.address</name>
  <value>${MASTER_IP}:50070</value>
</property>
<property>
  <name>dfs.namenode.plugins</name>
  <value>org.apache.hadoop.thriftfs.NamenodePlugin</value>
  <description>Comma-separated list of namenode plug-ins to be activated.
  </description>
</property>
<property>
  <name>dfs.datanode.plugins</name>
  <value>org.apache.hadoop.thriftfs.DatanodePlugin</value>
  <description>Comma-separated list of datanode plug-ins to be activated.
  </description>
</property>
<!-- we dont really care about being super safe -->
<property>
  <name>dfs.safemode.min.datanodes</name>
  <value>1</value>
</property>
<property>
  <name>dfs.safemode.extension</name>
  <value>5000</value>
  <description>
    Determines extension of safe mode in milliseconds
    after the threshold level is reached.
  </description>
</property>
</configuration>
END
  cat > $TARGET_DIR/mapred-site.xml <<END
<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
<property>
  <name>mapred.job.tracker</name>
  <value>${MASTER_IP}:8021</value>
</property>
<property>
  <name>mapred.job.tracker.http.address</name>
  <value>${MASTER_IP}:50030</value>
</property>
<property>
  <name>mapred.task.tracker.http.address</name>
  <value>${SLAVE_IP}:0</value>
</property>
<property>
  <name>mapred.jobtracker.plugins</name>
  <value>org.apache.hadoop.thriftfs.ThriftJobTrackerPlugin</value>
  <description>Comma-separated list of jobtracker plug-ins to be activated.
  </description>
</property>
<property>
  <name>mapred.system.dir</name>
  <value>/hadoop/mapred/system</value>
</property>
<property>
  <name>mapred.local.dir</name>
  <value>$TMP_DIR/mapred/local</value>
</property>
</configuration>
END

}

# Configure
function configure() {
  perl -p -i -e "s,localhost,$BIND_IP,g" desktop/conf/pseudo-distributed.ini
  mkdir -p $HADOOP_TMP_DIR
  write_hadoop_config $BIND_IP $BIND_IP $HADOOP_HOME/conf $HADOOP_TMP_DIR
  idx=0
  for slave in $SLAVE_IPS ; do
    idx=$[$idx + 1]
    datadir=$HADOOP_TMP_DIR-slave-$idx
    write_hadoop_config $slave $BIND_IP $HADOOP_HOME/conf-slave-$idx $datadir
  done
}

function start() {
  pushd $HADOOP_HOME
  export HADOOP_CLASSPATH=$GIT_ROOT/desktop/libs/hadoop/java-lib/\*
  if [ ! -d $HADOOP_TMP_DIR/dfs/name ]; then
    bin/hadoop namenode -format
  fi
  # Pass HADOOP_OPTS=$JDB_ON to any hadoop-daemon.sh to enable jdb
  JDB_ON="-Xdebug -Xrunjdwp:transport=dt_socket,address=8901,server=y,suspend=n"

  HADOOP_PID_DIR="$HADOOP_TMP_DIR-pids-master" \
    bin/hadoop-daemon.sh start namenode
  idx=0
  for ip in $SLAVE_IPS ; do
    idx=$[$idx + 1]
    HADOOP_PID_DIR="$HADOOP_TMP_DIR-pids-slave-$idx" \
      HADOOP_CONF_DIR="$HADOOP_HOME/conf-slave-$idx" \
      HADOOP_LOG_DIR="$HADOOP_HOME/logs-slave-$idx" \
      bin/hadoop-daemon.sh start datanode || true
  done
  bin/hadoop dfsadmin -safemode wait
  HADOOP_PID_DIR="$HADOOP_TMP_DIR-pids-master" \
    bin/hadoop-daemon.sh start secondarynamenode
  HADOOP_PID_DIR="$HADOOP_TMP_DIR-pids-master" \
    bin/hadoop-daemon.sh start jobtracker
  idx=0
  for ip in $SLAVE_IPS ; do
    idx=$[$idx + 1]
    HADOOP_PID_DIR="$HADOOP_TMP_DIR-pids-slave-$idx" \
      HADOOP_CONF_DIR="$HADOOP_HOME/conf-slave-$idx" \
      HADOOP_LOG_DIR="$HADOOP_HOME/logs-slave-$idx" \
      bin/hadoop-daemon.sh start tasktracker || true
  done
  popd
}

function stop() {
  pushd $HADOOP_HOME
  for daemon in namenode jobtracker; do
    HADOOP_PID_DIR="$HADOOP_TMP_DIR-pids-master" \
      bin/hadoop-daemon.sh stop $daemon
  done

  idx=0
  for ip in $SLAVE_IPS ; do
    idx=$[$idx + 1]
    HADOOP_PID_DIR="$HADOOP_TMP_DIR-pids-slave-$idx" \
      HADOOP_CONF_DIR="$HADOOP_HOME/conf-slave-$idx" \
      bin/hadoop-daemon.sh --config $HADOOP_HOME/conf-slave-$idx stop tasktracker || true
    HADOOP_PID_DIR="$HADOOP_TMP_DIR-pids-slave-$idx" \
      HADOOP_CONF_DIR="$HADOOP_HOME/conf-slave-$idx" \
       bin/hadoop-daemon.sh --config $HADOOP_HOME/conf-slave-$idx stop datanode || true
  done

  popd
}


pushd $GIT_ROOT

if [ ! -d .git ]; then
  echo "This script moves into your git root, but this has failed."
  exit 1
fi

if [ $# -eq 0 ]; then
  echo "Usage: $0 (all|checkout|build|build_jobsub|build_plugins|configure|start)"
  exit 1
fi

ARG=$1
shift 1
case $ARG
in
  configure|start|write_hadoop_config|stop)
    $ARG $@
    ;;
  all)
    configure
    start
    ;;
  *)
    echo "Unrecognized: $ARG"
    exit 1
  ;;
esac
