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


import atexit
import getpass
import logging
import os
import shutil
import signal
import subprocess
import socket
import tempfile
import textwrap
import time

import desktop
import hadoop
from hadoop.mini_cluster import find_unused_port, write_config
from hadoop.job_tracker import LiveJobTracker

# Shared global HDFS (for CDH4) and MR1 cluster.
_shared_cluster = None

LOG = logging.getLogger(__name__)

# Class to use for the cluster's GMSP.
CLUSTER_GMSP = 'org.apache.hadoop.security.StaticUserGroupMapping'

# users and their groups which are used in Hue tests.
TEST_USER_GROUP_MAPPING = {
   'test': ['test','users','supergroup'], 'chown_test': ['chown_test'],
   'notsuperuser': ['notsuperuser'], 'gamma': ['gamma'],
   'webui': ['webui'], 'hue': ['supergroup']
}

# How long we're willing to wait for the cluster to start
STARTUP_DEADLINE = 60.0

# Whether to cleanup afterwards
CLEANUP_TMP_DIR = os.environ.get("MINI_CLUSTER_CLEANUP", 'true')


class PseudoHdfs4(object):
  """This class runs HDFS (CDH4) and MR1 locally, in pseudo-distributed mode"""

  def __init__(self):
    self._tmpdir = tempfile.mkdtemp(prefix='tmp_hue_')
    self._superuser = getpass.getuser()
    self._fs = None
    self._jt = None

    self._mr1_env = None
    self._log_dir = None
    self._dfs_http_port = None
    self._dfs_http_address = None
    self._namenode_port = None
    self._fs_default_name = None

    self._jt_thrift_port = None
    self._jt_http_port = None
    self._jt_port = None
    self._tt_http_port = None

    self._nn_proc = None
    self._dn_proc = None
    self._jt_proc = None
    self._tt_proc = None
    self._fqdn = socket.getfqdn()

    self._core_site = None
    self._hdfs_site = None
    self._mapred_site = None

    self.shutdown_hook = None

  def __str__(self):
    return "PseudoHdfs4 (%(name)s) at %(dir)s --- MR1 (%(mapreduce)s) at http://%(fqdn)s:%(port)s" % {
      'name': self._fs_default_name,
      'dir': self._tmpdir,
      'mapreduce': self.mapred_job_tracker,
      'fqdn': self._fqdn,
      'port': self._jt_http_port}

  @property
  def superuser(self):
    return self._superuser

  @property
  def mr1_env(self):
    return self._mr1_env

  @property
  def log_dir(self):
    return self._log_dir

  @property
  def fs_default_name(self):
    return self._fs_default_name

  @property
  def namenode_port(self):
    return self._namenode_port

  @property
  def dfs_http_address(self):
    return self._dfs_http_address

  @property
  def dfs_http_port(self):
    return self._dfs_http_port

  @property
  def jt_thrift_port(self):
    return self._jt_thrift_port

  @property
  def mapred_job_tracker(self):
    return "%s:%s" % (self._fqdn, self._jt_port,)

  @property
  def mapred_job_tracker_http_address(self):
    return "%s:%s" % (self._fqdn, self._jt_http_port,)

  @property
  def hadoop_conf_dir(self):
    return self._tmppath('conf')

  @property
  def fs(self):
    """Returns a Filesystem object configured for this cluster."""
    if self._fs is None:
      if self._dfs_http_address is None:
        LOG.warn("Attempt to access uninitialized filesystem")
        return None
      self._fs = hadoop.fs.webhdfs.WebHdfs(
        "http://%s/webhdfs/v1" % (self._dfs_http_address,),
        self.fs_default_name)
    return self._fs

  @property
  def jt(self):
    """Returns a LiveJobTracker object configured for this cluster."""
    if self._jt is None:
      self._jt = LiveJobTracker(self._fqdn, self.jt_thrift_port)
    return self._jt

  def stop(self):
    """Kills the cluster ungracefully."""
    def _kill_proc(name, proc):
      try:
        while proc is not None and proc.poll() is None:
          os.kill(proc.pid, signal.SIGKILL)
          LOG.info('Stopping %s pid %s' % (name, proc.pid,))
          time.sleep(0.5)
      except Exception, ex:
        LOG.exception('Failed to stop pid %s. You may want to do it manually: %s' % (proc.pid, ex))

    _kill_proc('NameNode', self._nn_proc)
    _kill_proc('DataNode', self._dn_proc)
    _kill_proc('JobTracker', self._jt_proc)
    _kill_proc('TaskTracker', self._tt_proc)

    self._nn_proc = None
    self._dn_proc = None
    self._jt_proc = None
    self._tt_proc = None

    if CLEANUP_TMP_DIR == 'false':
      LOG.info('Skipping cleanup of temp directory "%s"' % (self._tmpdir,))
    else:
      LOG.info('Cleaning up temp directory "%s". '
               'Use "export MINI_CLUSTER_CLEANUP=false" to avoid.' % (self._tmpdir,))
      shutil.rmtree(self._tmpdir, ignore_errors=True)

    if self.shutdown_hook is not None:
      self.shutdown_hook()


  def _tmppath(self, filename):
    """Return a filepath inside temp dir"""
    return os.path.join(self._tmpdir, filename)

  def _logpath(self, filename):
    """Return a filepath inside log dir"""
    return os.path.join(self._log_dir, filename)

  def start(self):
    """Start the NN, DN, JT and TT processes"""
    LOG.info("Using temporary directory: %s" % (self._tmpdir,))

    # Fix up superuser group mapping
    if self.superuser not in TEST_USER_GROUP_MAPPING:
      TEST_USER_GROUP_MAPPING[self.superuser] = [self.superuser]

    # This is where we prepare our Hadoop configuration
    if not os.path.exists(self.hadoop_conf_dir):
      os.mkdir(self.hadoop_conf_dir)

    self._log_dir = self._tmppath('logs')
    if not os.path.exists(self._log_dir):
      os.mkdir(self._log_dir)

    # Write out the Hadoop conf files
    self._write_hadoop_metrics_conf(self.hadoop_conf_dir)
    self._write_core_site()
    self._write_hdfs_site()

    # More stuff to setup in the environment
    env = dict(
      HADOOP_HOME = hadoop.conf.HDFS_CLUSTERS['default'].HADOOP_HDFS_HOME.get(),
      HADOOP_BIN = hadoop.conf.HDFS_CLUSTERS['default'].HADOOP_BIN.get(),
      HADOOP_CONF_DIR = self.hadoop_conf_dir,
      HADOOP_HEAPSIZE = "128",
      HADOOP_LOG_DIR = self._log_dir,
      USER = self.superuser,
      LANG = "en_US.UTF-8",
      PATH = os.environ['PATH'],
    )

    if "JAVA_HOME" in os.environ:
      env['JAVA_HOME'] = os.environ['JAVA_HOME']

    LOG.debug("Hadoop Environment:\n" + "\n".join([ str(x) for x in sorted(env.items()) ]))

    # Format HDFS
    self._format(self.hadoop_conf_dir, env)

    # Run them
    self._nn_proc = self._start_daemon('namenode', self.hadoop_conf_dir, env)
    self._dn_proc = self._start_daemon('datanode', self.hadoop_conf_dir, env)

    # Make sure they're running
    deadline = time.time() + STARTUP_DEADLINE
    while not self._is_hdfs_ready(env):
      if time.time() > deadline:
        self.stop()
        raise RuntimeError('%s is taking too long to start' % (self,))
      time.sleep(5)

    # Start MR1
    self._start_mr1(env)

    # Make sure /tmp is 1777
    self.fs.setuser(self.superuser)
    if not self.fs.exists('/tmp'):
      self.fs.mkdir('/tmp', 01777)
    self.fs.chmod('/tmp', 01777)

    self.fs.chmod(self._tmpdir + '/hadoop_tmp_dir/mapred', 01777)
    self.fs.mkdir(self._tmpdir + '/hadoop_tmp_dir/mapred/staging', 01777)


  def _start_mr1(self, env):
    LOG.info("Starting MR1")

    # We need a different env because it's a different hadoop
    self._mr1_env = env.copy()
    self._mr1_env['HADOOP_HOME'] = hadoop.conf.MR_CLUSTERS['default'].HADOOP_MAPRED_HOME.get()
    self._mr1_env['HADOOP_BIN'] = hadoop.conf.MR_CLUSTERS['default'].HADOOP_BIN.get()
    self._mr1_env["HADOOP_CLASSPATH"] = ':'.join([
        hadoop.conf.HADOOP_PLUGIN_CLASSPATH.get(),
        # Due to CDH-4537, we need to add test dependencies to run minicluster
        os.path.join(os.path.dirname(__file__), 'test_jars', '*'),
      ])

    LOG.debug("MR1 Environment:\n" + "\n".join([ str(x) for x in sorted(self.mr1_env.items()) ]))

    # Configure
    self._write_mapred_site()

    # Run JT & TT
    self._jt_proc = self._start_daemon('jobtracker', self.hadoop_conf_dir, self.mr1_env)
    self._tt_proc = self._start_daemon('tasktracker', self.hadoop_conf_dir, self.mr1_env)

    # Make sure they're running
    deadline = time.time() + STARTUP_DEADLINE
    while not self._is_mr1_ready(self.mr1_env):
      if time.time() > deadline:
        self.stop()
        raise RuntimeError('%s is taking too long to start' % (self,))
      time.sleep(5)

  def _format(self, conf_dir, env):
    """Format HDFS"""
    args = (self._get_hadoop_bin(env),
            '--config', conf_dir,
            'namenode', '-format')
    LOG.info('Formatting HDFS: %s' % (args,))

    stdout = tempfile.TemporaryFile()
    stderr = tempfile.TemporaryFile()
    try:
      ret = subprocess.call(args, env=env, stdout=stdout, stderr=stderr)
      if ret != 0:
        stdout.seek(0)
        stderr.seek(0)
        raise RuntimeError('Failed to format namenode\n'
                           '=== Stdout ===:\n%s\n'
                           '=== Stderr ===:\n%s' %
                           (stdout.read(), stderr.read()))
    finally:
      stdout.close()
      stderr.close()

  def _log_exit(self, proc_name, exit_code):
    """Log the stdout and stderr for a process"""
    LOG.info('%s exited with %s' % (proc_name, exit_code))
    LOG.debug('--------------------- STDOUT:\n' +
              file(self._logpath(proc_name + '.stdout')).read())
    LOG.debug('--------------------- STDERR:\n' +
              file(self._logpath(proc_name + '.stderr')).read())

  def _is_hdfs_ready(self, env):
    """Whether HDFS is servicing requests"""
    if self._nn_proc.poll() is not None:
      self._log_exit('namenode', self._nn_proc.poll())
      return False
    if self._dn_proc.poll() is not None:
      self._log_exit('datanode', self._dn_proc.poll())
      return False

    # Run a `dfsadmin -report' against it
    dfsreport = subprocess.Popen(
      (self._get_hadoop_bin(env), 'dfsadmin', '-report'),
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      env=env)

    ret = dfsreport.wait()
    if ret != 0:
      LOG.debug('DFS not ready yet.\n%s\n%s' %
                (dfsreport.stderr.read(), dfsreport.stdout.read()))
      return False

    # Check that the DN is servicing
    report_out = dfsreport.stdout.read()
    if 'Datanodes available: 1' in report_out:
      return True
    LOG.debug('Waiting for DN to come up .................\n%s' % (report_out,))
    return False


  def _is_mr1_ready(self, env):
    """Whether MR1 is servicing requests"""
    if self._jt_proc.poll() is not None:
      self._log_exit('jobtracker', self._jt_proc.poll())
      return False
    if self._tt_proc.poll() is not None:
      self._log_exit('tasktracker', self._tt_proc.poll())
      return False

    # Run a `hadoop job -list all'
    list_all = subprocess.Popen(
      (self._get_hadoop_bin(env), 'job', '-list', 'all'),
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      env=env)

    ret = list_all.wait()
    if ret == 0:
      return True

    LOG.debug('MR1 not ready yet.\n%s\n%s' %
              (list_all.stderr.read(), list_all.stderr.read()))
    return False


  def _start_daemon(self, proc_name, conf_dir, env):
    """Start a hadoop daemon. Returns the Popen object."""
    hadoop_bin = self._get_hadoop_bin(env)
    args = (hadoop_bin,
            '--config', conf_dir,
            proc_name)
    LOG.info('Starting Hadoop cluster daemon: %s' % (args,))
    stdout = file(self._logpath(proc_name + ".stdout"), 'w')
    stderr = file(self._logpath(proc_name + ".stderr"), 'w')

    return subprocess.Popen(
      args=args,
      stdout=stdout,
      stderr=stderr,
      env=env)

  def _get_hadoop_bin(self, env):
    try:
      return env['HADOOP_BIN']
    except KeyError:
      return os.path.join(env['HADOOP_HOME'], 'bin', 'hadoop')

  def _write_hdfs_site(self):
    self._dfs_http_port = find_unused_port()
    self._dfs_http_address = '%s:%s' % (self._fqdn, self._dfs_http_port)

    hdfs_configs = {
      'dfs.webhdfs.enabled': 'true',
      'dfs.http.address': self._dfs_http_address,
      'dfs.namenode.safemode.extension': 1,
      'dfs.namenode.safemode.threshold-pct': 0,
      'dfs.datanode.address': '%s:0' % self._fqdn,
      # Work around webhdfs redirect bug -- bind to all interfaces
      'dfs.datanode.http.address': '0.0.0.0:0',
      'dfs.datanode.ipc.address': '%s:0' % self._fqdn,
      'dfs.replication': 1,
      'dfs.safemode.min.datanodes': 1,
      'dfs.namenode.fs-limits.min-block-size': '1000',
      'dfs.permissions': 'true'
    }
    self._hdfs_site = self._tmppath('conf/hdfs-site.xml')
    write_config(hdfs_configs, self._hdfs_site)

  def _write_core_site(self):
    # Prep user group mapping file
    ugm_properties = self._tmppath('ugm.properties')
    self._write_static_group_mapping(ugm_properties)
    self._namenode_port = find_unused_port()
    self._fs_default_name = 'hdfs://%s:%s' % (self._fqdn, self._namenode_port,)

    core_configs = {
      'fs.default.name': self._fs_default_name,
      'hadoop.security.authorization': 'true',
      'hadoop.security.authentication': 'simple',
      'hadoop.proxyuser.hue.hosts': '*',
      'hadoop.proxyuser.hue.groups': '*',
      'hadoop.proxyuser.%s.hosts' % (getpass.getuser(),): '*',
      'hadoop.proxyuser.%s.groups' % (getpass.getuser(),): '*',
      'hadoop.tmp.dir': self._tmppath('hadoop_tmp_dir'),
      'fs.trash.interval': 10
    }
    self._core_site = self._tmppath('conf/core-site.xml')
    write_config(core_configs, self._core_site)

  def _write_mapred_site(self):
    self._jt_thrift_port = find_unused_port()
    self._jt_http_port = find_unused_port()
    self._jt_port = find_unused_port()
    self._tt_http_port = find_unused_port()

    mapred_configs = {
      'mapred.job.tracker': '%s:%s' % (self._fqdn, self._jt_port,),
      'mapred.job.tracker.http.address': '%s:%s' % (self._fqdn, self._jt_http_port,),
      'jobtracker.thrift.address': '%s:%s' % (self._fqdn, self._jt_thrift_port,),
      'mapred.jobtracker.plugins': 'org.apache.hadoop.thriftfs.ThriftJobTrackerPlugin',
      'mapred.task.tracker.http.address': '%s:%s' % (self._fqdn, self._tt_http_port,),
    }
    self._mapred_site = self._tmppath('conf/mapred-site.xml')
    write_config(mapred_configs, self._tmppath('conf/mapred-site.xml'))

  def _write_hadoop_metrics_conf(self, conf_dir):
    f = file(os.path.join(conf_dir, "hadoop-metrics.properties"), "w")
    try:
      f.write(textwrap.dedent("""
          dfs.class=org.apache.hadoop.metrics.spi.NoEmitMetricsContext
          mapred.class=org.apache.hadoop.metrics.spi.NoEmitMetricsContext
          jvm.class=org.apache.hadoop.metrics.spi.NoEmitMetricsContext
          rpc.class=org.apache.hadoop.metrics.spi.NoEmitMetricsContext
          """))
    finally:
      f.close()

  def _write_static_group_mapping(self, filename):
    f = file(filename, 'w')
    try:
      for user, groups in TEST_USER_GROUP_MAPPING.iteritems():
        f.write('%s = %s\n' % (user, ','.join(groups)))
    finally:
      f.close()


def shared_cluster():
  """Create a shared cluster"""
  global _shared_cluster
  if _shared_cluster is None:
    cluster = PseudoHdfs4()
    atexit.register(cluster.stop)
    try:
      cluster.start()
    except Exception, ex:
      LOG.exception("Failed to fully bring up test cluster: %s" % (ex,))

    # Fix config to reflect the cluster setup.
    fqdn = socket.getfqdn()
    webhdfs_url = "http://%s:%s/webhdfs/v1" % (fqdn, cluster.dfs_http_port,)
    closers = [
      hadoop.conf.HDFS_CLUSTERS['default'].FS_DEFAULTFS.set_for_testing(cluster.fs_default_name),
      hadoop.conf.HDFS_CLUSTERS['default'].WEBHDFS_URL.set_for_testing(webhdfs_url),
      hadoop.conf.HDFS_CLUSTERS['default'].HADOOP_CONF_DIR.set_for_testing(cluster.hadoop_conf_dir),
      hadoop.conf.MR_CLUSTERS['default'].HOST.set_for_testing(fqdn),
      hadoop.conf.MR_CLUSTERS['default'].PORT.set_for_testing(cluster._jt_port),
      hadoop.conf.MR_CLUSTERS['default'].JT_THRIFT_PORT.set_for_testing(cluster.jt_thrift_port),
      hadoop.conf.MR_CLUSTERS['default'].HADOOP_CONF_DIR.set_for_testing(cluster.hadoop_conf_dir),
    ]

    old = hadoop.cluster.clear_caches()

    def restore_config():
      hadoop.cluster.restore_caches(old)
      for x in closers:
        x()

    cluster.shutdown_hook = restore_config
    _shared_cluster = cluster

  return _shared_cluster


#
# Simply try to exercise it
#
if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG)
  desktop.lib.conf.initialize([hadoop.conf])

  cluster = PseudoHdfs4()
  cluster.start()
  LOG.info("%s running" % (cluster,))
  LOG.info("fs.default.name=%s" % (cluster.fs_default_name,))
  LOG.info("dfs.http.address=%s" % (cluster.dfs_http_address,))
  LOG.info("jobtracker.thrift.port=%s" % (cluster.jt_thrift_port,))
  LOG.info("mapred.job.tracker=%s" % (cluster.mapred_job_tracker,))

  from IPython.Shell import IPShellEmbed
  IPShellEmbed()()
  cluster.stop()
