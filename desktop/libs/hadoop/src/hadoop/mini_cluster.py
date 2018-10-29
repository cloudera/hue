#!/usr/bin/env python
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


#######################################################
##               WARNING!!!                          ##
##   This file is stale. Hadoop 0.23 and CDH4        ##
##   do not support minicluster. This is replaced    ##
##   by webhdfs.py, to set up a running cluster.     ##
#######################################################


# A Python-side driver for MiniHadoopClusterManager
# 
# See README.testing for hints on how to use this,
# and also look for other examples.
#
# If you have one of these running and want to figure out what ports
# are open, one way to do so is something like:
# for p in $(lsof -p 63564 | grep LISTEN | sed -e 's/.*:\([0-9][0-9]*\).*/\1/')
# do
#   echo $p
#   echo "GET /" | nc -w 1 localhost $p
# done

import atexit
import subprocess
import os
import pwd
import logging
import sys
import signal
import shutil
import time
import tempfile
import json
import lxml.etree
import urllib2

from desktop.lib import python_util
from desktop.lib.test_utils import clear_sys_caches, restore_sys_caches

import hadoop.cluster

# Starts mini cluster suspended until a debugger attaches to it.
DEBUG_HADOOP=False
# Redirects mini cluster stderr to stderr.  (Default is to put it in a file.)
USE_STDERR=os.environ.get("MINI_CLUSTER_USE_STDERR", False)
# Whether to clean up temp dir at exit
CLEANUP_TMP_DIR=os.environ.get("MINI_CLUSTER_CLEANUP", True)
# How long to wait for cluster to start up.  (seconds)
MAX_CLUSTER_STARTUP_TIME = 120.0
# List of classes to be used as plugins for the JT of the cluster.
CLUSTER_JT_PLUGINS = 'org.apache.hadoop.thriftfs.ThriftJobTrackerPlugin'
# MR Task Scheduler. By default use the FIFO scheduler
CLUSTER_TASK_SCHEDULER='org.apache.hadoop.mapred.JobQueueTaskScheduler'
# MR queue names
CLUSTER_QUEUE_NAMES='default'

STARTUP_CONFIGS={}

# users and their groups which are used in Hue tests.
TEST_USER_GROUP_MAPPING = {
   'test': ['test','users','supergroup'], 'chown_test': ['chown_test'],
   'notsuperuser': ['notsuperuser'], 'gamma': ['gamma'],
   'webui': ['webui'], 'hue': ['supergroup']
}

LOGGER=logging.getLogger(__name__)


class MiniHadoopCluster(object):
  """
  Manages the invocation of a MiniHadoopClusterManager from Python.
  """
  def __init__(self, num_datanodes=1, num_tasktrackers=1):
    # These are cached
    self._jt, self._fs = None, None
    self.num_datanodes = num_datanodes
    self.num_tasktrackers = num_tasktrackers

  def start(self, extra_configs=None):
    """
    Start a cluster as a subprocess.
    """
    self.tmpdir = tempfile.mkdtemp()

    if not extra_configs:
      extra_configs = {}

    def tmppath(filename):
      """Creates paths in tmpdir."""
      return os.path.join(self.tmpdir, filename)

    LOGGER.info("Using temporary directory: %s" % self.tmpdir)

    in_conf_dir = tmppath("in-conf")
    os.mkdir(in_conf_dir)
    self.log_dir = tmppath("logs")
    os.mkdir(self.log_dir)
    f = file(os.path.join(in_conf_dir, "hadoop-metrics.properties"), "w")
    try:
      f.write("""
dfs.class=org.apache.hadoop.metrics.spi.NoEmitMetricsContext
mapred.class=org.apache.hadoop.metrics.spi.NoEmitMetricsContext
jvm.class=org.apache.hadoop.metrics.spi.NoEmitMetricsContext
rpc.class=org.apache.hadoop.metrics.spi.NoEmitMetricsContext
""")
    finally:
      f.close()

    if self.superuser not in TEST_USER_GROUP_MAPPING:
      TEST_USER_GROUP_MAPPING[self.superuser] = [self.superuser]

    _write_static_group_mapping(TEST_USER_GROUP_MAPPING,
      tmppath('ugm.properties'))

    core_configs = {
      'hadoop.proxyuser.%s.groups' % (self.superuser,): 'users,supergroup',
      'hadoop.proxyuser.%s.hosts' % (self.superuser,): 'localhost',
      'mapred.jobtracker.plugins': CLUSTER_JT_PLUGINS}

    extra_configs.update(STARTUP_CONFIGS)
    write_config(core_configs, tmppath('in-conf/core-site.xml'))

    write_config({'mapred.jobtracker.taskScheduler': CLUSTER_TASK_SCHEDULER,
                  'mapred.queue.names': CLUSTER_QUEUE_NAMES},
                 tmppath('in-conf/mapred-site.xml'))

    hadoop_policy_keys = ['client', 'client.datanode', 'datanode', 'inter.datanode', 'namenode', 'inter.tracker', 'job.submission', 'task.umbilical', 'refresh.policy', 'admin.operations']
    hadoop_policy_config = {}
    for policy in hadoop_policy_keys:
      hadoop_policy_config['security.' + policy + '.protocol.acl'] = '*'
    write_config(hadoop_policy_config, tmppath('in-conf/hadoop-policy.xml'))

    details_file = file(tmppath("details.json"), "w+")
    try:
      args = [ os.path.join(hadoop.conf.HADOOP_MR1_HOME.get(), 'bin', 'hadoop'),
        "jar",
        hadoop.conf.HADOOP_TEST_JAR.get(),
        "minicluster",
        "-writeConfig", tmppath("config.xml"),
        "-writeDetails", tmppath("details.json"),
        "-datanodes", str(self.num_datanodes),
        "-tasktrackers", str(self.num_tasktrackers),
        "-useloopbackhosts",
        "-D", "hadoop.tmp.dir=%s" % self.tmpdir,
        "-D", "mapred.local.dir=%s/mapred/local" % self.tmpdir,
        "-D", "mapred.system.dir=/mapred/system",
        "-D", "mapred.temp.dir=/mapred/temp",
        "-D", "jobclient.completion.poll.interval=100",
        "-D", "jobclient.progress.monitor.poll.interval=100",
        "-D", "fs.checkpoint.period=1",
        # For a reason I don't fully understand, this must be 0.0.0.0 and not 'localhost'
        "-D", "dfs.secondary.http.address=0.0.0.0:%d" % python_util.find_unused_port(),
        # We bind the NN's thrift interface to a port we find here.
        # This is suboptimal, since there's a race.  Alas, if we don't
        # do this here, the datanodes fail to discover the namenode's thrift
        # address, and there's a race there
        "-D", "dfs.thrift.address=localhost:%d" % python_util.find_unused_port(),
        "-D", "jobtracker.thrift.address=localhost:%d" % python_util.find_unused_port(),
        # Jobs realize they have finished faster with this timeout.
        "-D", "jobclient.completion.poll.interval=50",
        "-D", "hadoop.security.authorization=true",
        "-D", "hadoop.policy.file=%s/hadoop-policy.xml" % in_conf_dir,
      ]

      for key,value in extra_configs.iteritems():
        args.append("-D")
        args.append(key + "=" + value)

      env = {}
      env["HADOOP_CONF_DIR"] = in_conf_dir
      env["HADOOP_OPTS"] = "-Dtest.build.data=%s" % (self.tmpdir, )
      env["HADOOP_CLASSPATH"] = ':'.join([
        # -- BEGIN JAVA TRIVIA --
        # Add the -test- jar to the classpath to work around a subtle issue
        # involving Java classloaders. In brief, hadoop's RunJar class creates
        # a child classloader with the test jar on it, but the core classes
        # are loaded by the system classloader. This is fine except that
        # some classes in the test jar extend package-protected classes in the
        # core jar. Even though the classes are in the same package name, they
        # are thus loaded by different classloaders and therefore an IllegalAccessError
        # prevents the MiniMRCluster from starting. Adding the test jar to the system
        # classpath prevents this error since then both the MiniMRCluster and the
        # core classes are loaded by the system classloader.
        hadoop.conf.HADOOP_TEST_JAR.get(),
        # -- END JAVA TRIVIA --
        hadoop.conf.HADOOP_PLUGIN_CLASSPATH.get(),
        # Due to CDH-4537, we need to add test dependencies to run minicluster
        os.path.join(os.path.dirname(__file__), 'test_jars', '*'),
      ])
      env["HADOOP_HEAPSIZE"] = "128"
      env["HADOOP_HOME"] = hadoop.conf.HADOOP_MR1_HOME.get()
      env["HADOOP_LOG_DIR"] = self.log_dir
      env["USER"] = self.superuser
      if "JAVA_HOME" in os.environ:
        env["JAVA_HOME"] = os.environ["JAVA_HOME"]
      # Wait for the debugger to attach
      if DEBUG_HADOOP:
        env["HADOOP_OPTS"] = env.get("HADOOP_OPTS", "") + " -Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=y,address=9999"

      if USE_STDERR:
        stderr=sys.stderr
      else:
        stderr=file(tmppath("stderr"), "w")
      LOGGER.debug("Starting minicluster: %s env: %s" % (repr(args), repr(env)))
      self.clusterproc = subprocess.Popen(
        args=args,
        stdout=file(tmppath("stdout"), "w"),
        stderr=stderr,
        env=env)

      details = {}
      start = time.time()
      # We consider the cluster started when the details file parses correct JSON.
      # MiniHadoopCluster currently writes the details file last, and this depends
      # on that.
      while not details:
        try:
          details_file.seek(0)
          details = json.load(details_file)
        except ValueError:
          pass
        if self.clusterproc.poll() is not None or (not DEBUG_HADOOP and (time.time() - start) > MAX_CLUSTER_STARTUP_TIME):
          LOGGER.debug("stdout:" + file(tmppath("stdout")).read())
          if not USE_STDERR:
            LOGGER.debug("stderr:" + file(tmppath("stderr")).read())
          self.stop()
          raise Exception("Cluster process quit or is taking too long to start.  Aborting.")
    finally:
      details_file.close()

    LOGGER.debug("Successfully started minicluster")

    # Place all the details as attributes on self.
    for k, v in details.iteritems():
      setattr(self, k, v)

    # Parse the configuration using XPath and place into self.config.
    config = lxml.etree.parse(tmppath("config.xml"))
    self.config = dict( (property.find("./name").text, property.find("./value").text)
      for property in config.xpath("/configuration/property"))

    # Write out Hadoop-style configuration directory, 
    # which can, in turn, be used for /bin/hadoop.
    self.config_dir = tmppath("conf")
    os.mkdir(self.config_dir)

    hadoop.conf.HADOOP_CONF_DIR.set_for_testing(self.config_dir)

    write_config(self.config, tmppath("conf/core-site.xml"),
      ["fs.defaultFS", "jobclient.completion.poll.interval",
       "dfs.namenode.checkpoint.period", "dfs.namenode.checkpoint.dir",
       'hadoop.proxyuser.'+self.superuser+'.groups', 'hadoop.proxyuser.'+self.superuser+'.hosts'])
    write_config(self.config, tmppath("conf/hdfs-site.xml"), ["fs.defaultFS", "dfs.namenode.http-address", "dfs.namenode.secondary.http-address"])
    # mapred.job.tracker isn't written out into self.config, so we fill
    # that one out more manually.
    write_config({ 'mapred.job.tracker': 'localhost:%d' % self.jobtracker_port },
                 tmppath("conf/mapred-site.xml"))
    write_config(hadoop_policy_config, tmppath('conf/hadoop-policy.xml'))

    # Once the config is written out, we can start the 2NN.
    args = [hadoop.conf.HADOOP_BIN.get(),
      '--config', self.config_dir,
      'secondarynamenode']

    LOGGER.debug("Starting 2NN at: " +
      self.config['dfs.secondary.http.address'])
    LOGGER.debug("2NN command: %s env: %s" % (repr(args), repr(env)))

    self.secondary_proc = subprocess.Popen(
      args=args,
      stdout=file(tmppath("stdout.2nn"), "w"),
      stderr=file(tmppath("stderr.2nn"), "w"),
      env=env)

    while True:
      try:
        response = urllib2.urlopen(urllib2.Request('http://' +
          self.config['dfs.secondary.http.address']))
      except urllib2.URLError:
        # If we should abort startup.
        if self.secondary_proc.poll() is not None or (not DEBUG_HADOOP and (time.time() - start) > MAX_CLUSTER_STARTUP_TIME):
          LOGGER.debug("stdout:" + file(tmppath("stdout")).read())
          if not USE_STDERR:
            LOGGER.debug("stderr:" + file(tmppath("stderr")).read())
          self.stop()
          raise Exception("2nn process quit or is taking too long to start. Aborting.")
          break
        else:
          time.sleep(1)
          continue

      # We didn't get a URLError. 2NN started successfully.
      response.close()
      break

    LOGGER.debug("Successfully started 2NN")


  def stop(self):
    """
    Kills the cluster ungracefully.
    """
    if self.clusterproc and self.clusterproc.poll() is None:
      os.kill(self.clusterproc.pid, signal.SIGKILL)
      self.clusterproc.wait()

    if self.secondary_proc and self.secondary_proc.poll() is None:
      os.kill(self.secondary_proc.pid, signal.SIGKILL)
      self.secondary_proc.wait()

    if CLEANUP_TMP_DIR != 'false':
      logging.info("Cleaning up self.tmpdir.  Use $MINI_CLUSTER_CLEANUP to avoid.")
      shutil.rmtree(self.tmpdir)

  @property
  def fs(self):
    # Deprecated
    return None

  @property
  def jt(self):
    # Deprecated
    return None

  @property
  def superuser(self):
    """
    Returns the "superuser" of this cluster.  
    
    This is essentially the user that the cluster was started
    with.
    """
    return pwd.getpwuid(os.getuid()).pw_name

  @property
  def namenode_thrift_port(self):
    """
    Return the namenode thrift port.
    """
    _, port = self.config["dfs.thrift.address"].split(":")
    return int(port)

  @property
  def jobtracker_thrift_port(self):
    """
    Return the jobtracker thrift port.
    """
    _, port = self.config["jobtracker.thrift.address"].split(":")
    return int(port)

  def dump_ini(self, fd=sys.stdout):
    """
    Dumps an ini-style configuration suitable for configuring desktop
    to talk to this cluster.
    TODO(todd) eventually this should use config framework 'writeback'
    support

    @param fd: a file-like writable object
    """
    print >>fd, "[hadoop]"
    print >>fd, "[[hdfs_clusters]]"
    print >>fd, "[[[default]]]"
    print >>fd, "thrift_port=%d" % self.namenode_thrift_port
    print >>fd, "[[mapred_clusters]]"
    print >>fd, "[[[default]]]"
    print >>fd, "thrift_port=%d" % self.jobtracker_thrift_port


# Shared global cluster returned by shared_cluster context manager.
_shared_cluster = None

def shared_cluster(conf=False):
  """
  Use a shared cluster that is initialized on demand,
  and that is torn down at process exit.

  If conf is True, then configuration is updated to
  reference the cluster, and relevant caches are cleared.

  Returns a lambda which must be called when you are
  done with the shared cluster.
  """
  cluster = shared_cluster_internal()
  closers = [ ]
  if conf:
    closers.extend([
      hadoop.conf.HDFS_CLUSTERS["default"].NN_HOST.set_for_testing("localhost"),
      hadoop.conf.HDFS_CLUSTERS["default"].NN_HDFS_PORT.set_for_testing(cluster.namenode_port),
      hadoop.conf.MR_CLUSTERS["default"].HOST.set_for_testing("localhost"),
      hadoop.conf.MR_CLUSTERS["default"].JT_THRIFT_PORT.set_for_testing(cluster.jt.thrift_port),
    ])
    # Clear the caches
    # This is djanky (that's django for "janky").
    # Caches are tricky w.r.t. to to testing;
    # perhaps there are better patterns?
    old_caches = clear_sys_caches()

  def finish():
    if conf:
      restore_sys_caches(old_caches)
    for x in closers:
      x()

  # We don't run the cluster's real stop method,
  # because a shared cluster should be shutdown at 
  # exit.
  cluster.shutdown = finish
  return cluster

def write_config(config, path, variables=None):
  """
  Minimal utility to write Hadoop-style configuration
  from a configuration map (config), into a new file
  called path.
  """
  f = file(path, "w")
  try:
    f.write("""<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
""")
    keys = (variables and (variables,) or (config.keys(),))[0]
    for name in keys:
      value = config[name]
      f.write("  <property>\n")
      f.write("    <name>%s</name>\n" % name)
      f.write("    <value>%s</value>\n" % value)
      f.write("  </property>\n")
    f.write("</configuration>\n")
  finally:
    f.close()

def _write_static_group_mapping(user_group_mapping, path):
  """
  Create a Java-style .properties file to contain the static user -> group
  mapping used by tests.
  """
  f = file(path, 'w')
  try:
    for user, groups in user_group_mapping.iteritems():
      f.write('%s = %s\n' % (user, ','.join(groups)))
  finally:
    f.close()

def shared_cluster_internal():
  """
  Manages _shared_cluster.
  """
  global _shared_cluster
  if _shared_cluster is None:
    _shared_cluster = MiniHadoopCluster()
    _shared_cluster.start()
    atexit.register(_shared_cluster.stop)
  return _shared_cluster

if __name__ == '__main__':
  """
  It's poor form to write tests for tests (the world-wide stack
  overflow exception), so this merely tries the code.
  """
  logging.basicConfig(level=logging.DEBUG)
  import desktop
  desktop.lib.conf.initialize([hadoop.conf])

  if True:
    cluster = MiniHadoopCluster(num_datanodes=5, num_tasktrackers=5)
    cluster.start()
    print cluster.namenode_port
    print cluster.jobtracker_port
    print cluster.config.get("dfs.thrift.address")
    cluster.dump_ini(sys.stdout)

    from IPython.Shell import IPShellEmbed
    IPShellEmbed()()
    cluster.stop()
