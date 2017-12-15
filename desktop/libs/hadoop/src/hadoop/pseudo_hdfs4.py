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

from desktop.lib.paths import get_run_root
from desktop.lib.python_util import find_unused_port
from desktop.lib.test_utils import clear_sys_caches, restore_sys_caches

import hadoop
from hadoop import cluster
from hadoop.mini_cluster import write_config


_shared_cluster = None

LOG = logging.getLogger(__name__)


STARTUP_DEADLINE = 60.0
CLEANUP_TMP_DIR = os.environ.get('MINI_CLUSTER_CLEANUP', 'true')
TEST_HDFS_TMP_DIR = os.environ.get('TEST_HDFS_TMP_DIR')


def is_live_cluster():
  return os.environ.get('LIVE_CLUSTER', 'false').lower() == 'true'

def get_fs_prefix(fs):
  prefix = '/tmp/hue_tests_%s' % str(time.time())
  fs.mkdir(prefix, 0777)
  return prefix

def get_db_prefix(name='hive'):
  if is_live_cluster():
    return 'hue_test_%s_%s' % (name, str(time.time()).replace('.', ''))
  else:
    return 'default'


class LiveHdfs():
  def __init__(self):
    self.fs = cluster.get_hdfs('default')
    # Assumes /tmp exists and is 1777
    self.jt = None # Deprecated

    self.fs_prefix = get_fs_prefix(self.fs)
    LOG.info('Using %s as FS root' % self.fs_prefix)

    # Might need more
    self.fs.do_as_user('test', self.fs.create_home_dir, '/user/test')
    self.fs.do_as_user('hue', self.fs.create_home_dir, '/user/hue')

  @property
  def superuser(self):
    return self.fs.superuser


class PseudoHdfs4(object):
  """Run HDFS and MR2 locally, in pseudo-distributed mode"""

  def __init__(self):
    self._tmpdir = tempfile.mkdtemp(prefix='tmp_hue_', dir=TEST_HDFS_TMP_DIR)
    os.chmod(self._tmpdir, 0755)
    self._superuser = getpass.getuser()
    self.fs_prefix = None

    self._fs = None
    self._jt = None

    self._mr2_env = None
    self._log_dir = None
    self._dfs_http_port = None
    self._dfs_http_address = None
    self._namenode_port = None
    self._fs_default_name = None

    self._rm_port = None

    self._nn_proc = None
    self._dn_proc = None
    self._rm_proc = None
    self._nm_proc = None
    self._hs_proc = None

    self._fqdn = socket.getfqdn()

    self._core_site = None
    self._hdfs_site = None
    self._mapred_site = None

    self.shutdown_hook = None

  def __str__(self):
    return "PseudoHdfs5 (%(name)s) at %(dir)s --- MR2 (%(mapreduce)s) at http://%(fqdn)s:%(port)s" % {
      'name': self._fs_default_name,
      'dir': self._tmpdir,
      'mapreduce': self.mapred_job_tracker,
      'fqdn': self._fqdn,
      'port': self._rm_port
    }

  @property
  def superuser(self):
    return self._superuser

  @property
  def mr2_env(self):
    return self._mr2_env

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
  def mapred_job_tracker(self):
    return "%s:%s" % (self._fqdn, self._rm_port,)

  @property
  def hadoop_conf_dir(self):
    return self._tmppath('conf')

  @property
  def fs(self):
    if self._fs is None:
      if self._dfs_http_address is None:
        LOG.warn("Attempt to access uninitialized filesystem")
        return None
      self._fs = hadoop.fs.webhdfs.WebHdfs("http://%s/webhdfs/v1" % (self._dfs_http_address,), self.fs_default_name)
    return self._fs

  @property
  def jt(self):
    return None

  def stop(self):
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
    _kill_proc('ResourceManager', self._rm_proc)
    _kill_proc('Nodemanager', self._nm_proc)
    _kill_proc('HistoryServer', self._hs_proc)

    self._nn_proc = None
    self._dn_proc = None
    self._rm_proc = None
    self._nm_proc = None
    self._hs_proc = None

    if CLEANUP_TMP_DIR == 'false':
      LOG.info('Skipping cleanup of temp directory "%s"' % (self._tmpdir,))
    else:
      LOG.info('Cleaning up temp directory "%s". Use "export MINI_CLUSTER_CLEANUP=false" to avoid.' % (self._tmpdir,))
      shutil.rmtree(self._tmpdir, ignore_errors=True)

    if self.shutdown_hook is not None:
      self.shutdown_hook()


  def _tmppath(self, filename):
    return os.path.join(self._tmpdir, filename)

  def _logpath(self, filename):
    return os.path.join(self._log_dir, filename)

  def start(self):
    LOG.info("Using temporary directory: %s" % (self._tmpdir,))

    if not os.path.exists(self.hadoop_conf_dir):
      os.mkdir(self.hadoop_conf_dir)

    self._log_dir = self._tmppath('logs')
    if not os.path.exists(self._log_dir):
      os.mkdir(self._log_dir)

    self._local_dir = self._tmppath('local')
    if not os.path.exists(self._local_dir):
      os.mkdir(self._local_dir)

    self._write_hadoop_metrics_conf(self.hadoop_conf_dir)
    self._write_core_site()
    self._write_hdfs_site()
    self._write_yarn_site()
    self._write_mapred_site()

    # More stuff to setup in the environment
    env = {
      'YARN_HOME': get_run_root('ext/hadoop/hadoop'),
      'HADOOP_COMMON_HOME': get_run_root('ext/hadoop/hadoop'),
      'HADOOP_MAPRED_HOME': get_run_root('ext/hadoop/hadoop'),
      'HADOOP_HDFS_HOME': get_run_root('ext/hadoop/hadoop'),

      'HADOOP_CONF_DIR': self.hadoop_conf_dir,
      'YARN_CONF_DIR': self.hadoop_conf_dir,

      'HADOOP_HEAPSIZE': '128',
      'HADOOP_LOG_DIR': self._log_dir,
      'USER': self.superuser,
      'LANG': "en_US.UTF-8",
      'PATH': os.environ['PATH'],
    }

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

    # Start MR2
    self._start_mr2(env)

    # Create HDFS directories
    if not self.fs.exists('/tmp'):
      self.fs.do_as_superuser(self.mkdir, '/tmp', 01777)
    self.fs.do_as_superuser(self.fs.chmod, '/tmp', 01777)

    self.fs.do_as_superuser(self.fs.mkdir, '/tmp/hadoop-yarn', 01777)
    self.fs.do_as_superuser(self.fs.chmod, '/tmp/hadoop-yarn', 01777)

    self.fs.do_as_superuser(self.fs.mkdir, '/tmp/hadoop-yarn/staging', 01777)
    self.fs.do_as_superuser(self.fs.chmod, '/tmp/hadoop-yarn/staging', 01777)

    self.fs.do_as_superuser(self.fs.mkdir, '/tmp/hadoop-yarn/staging/history', 01777)
    self.fs.do_as_superuser(self.fs.chmod, '/tmp/hadoop-yarn/staging/history', 01777)

    self.fs.do_as_superuser(self.fs.mkdir, '/tmp/hadoop-yarn/staging/history/done', 01777)
    self.fs.do_as_superuser(self.fs.chmod, '/tmp/hadoop-yarn/staging/history/done', 01777)

    self.fs.do_as_superuser(self.fs.mkdir, '/tmp/hadoop-yarn/staging/history/done/2015', 01777)
    self.fs.do_as_superuser(self.fs.chmod, '/tmp/hadoop-yarn/staging/history/done/2015', 01777)

    self.fs.do_as_superuser(self.fs.mkdir, '/var/log/hadoop-yarn/apps', 01777)
    self.fs.do_as_superuser(self.fs.chmod, '/var/log/hadoop-yarn/apps', 01777)

    self.fs.do_as_user('test', self.fs.create_home_dir, '/user/test')
    self.fs.do_as_user('hue', self.fs.create_home_dir, '/user/hue')

    self.fs_prefix = get_fs_prefix(self.fs)


  def _start_mr2(self, env):
    LOG.info("Starting MR2")

    self._mr2_env = env.copy()

    LOG.debug("MR2 Environment:\n" + "\n".join([ str(x) for x in sorted(self.mr2_env.items()) ]))

    # Run YARN
    self._rm_proc = self._start_daemon('resourcemanager', self.hadoop_conf_dir, self.mr2_env, self._get_yarn_bin(self.mr2_env))
    self._nm_proc = self._start_daemon('nodemanager', self.hadoop_conf_dir, self.mr2_env, self._get_yarn_bin(self.mr2_env))
    self._hs_proc = self._start_daemon('historyserver', self.hadoop_conf_dir, self.mr2_env, self._get_mapred_bin(self.mr2_env))

    # Give them a moment to actually start
    time.sleep(1)

    # Make sure they're running
    deadline = time.time() + STARTUP_DEADLINE
    while not self._is_mr2_ready(self.mr2_env):
      if time.time() > deadline:
        self.stop()
        raise RuntimeError('%s is taking too long to start' % (self,))
      time.sleep(5)

  def _format(self, conf_dir, env):
    args = (self._get_hdfs_bin(env), '--config', conf_dir, 'namenode', '-format')
    LOG.info('Formatting HDFS: %s' % (args,))

    stdout = tempfile.TemporaryFile()
    stderr = tempfile.TemporaryFile()
    try:
      ret = subprocess.call(args, env=env, stdout=stdout, stderr=stderr)
      if ret != 0:
        stdout.seek(0)
        stderr.seek(0)
        raise RuntimeError('Failed to format namenode\n''=== Stdout ===:\n%s\n''=== Stderr ===:\n%s' % (stdout.read(), stderr.read()))
    finally:
      stdout.close()
      stderr.close()

  def _log_exit(self, proc_name, exit_code):
    LOG.info('%s exited with %s' % (proc_name, exit_code))
    LOG.debug('--------------------- STDOUT:\n' + file(self._logpath(proc_name + '.stdout')).read())
    LOG.debug('--------------------- STDERR:\n' + file(self._logpath(proc_name + '.stderr')).read())

  def _is_hdfs_ready(self, env):
    if self._nn_proc.poll() is not None:
      self._log_exit('namenode', self._nn_proc.poll())
      return False
    if self._dn_proc.poll() is not None:
      self._log_exit('datanode', self._dn_proc.poll())
      return False

    # Run a `dfsadmin -report' against it
    dfsreport = subprocess.Popen((self._get_hdfs_bin(env), 'dfsadmin', '-report'),
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      env=env)

    ret = dfsreport.wait()
    if ret != 0:
      LOG.debug('DFS not ready yet.\n%s\n%s' % (dfsreport.stderr.read(), dfsreport.stdout.read()))
      return False

    # Check that the DN is servicing
    report_out = dfsreport.stdout.read()
    if 'Live datanodes (1)' in report_out:
      return True
    LOG.debug('Waiting for DN to come up .................\n%s' % (report_out,))
    return False


  def _is_mr2_ready(self, env):
    if self._rm_proc.poll() is not None:
      self._log_exit('resourcemanager', self._rm_proc.poll())
      return False
    if self._nm_proc.poll() is not None:
      self._log_exit('nodemanager', self._nm_proc.poll())
      return False
    if self._hs_proc.poll() is not None:
      self._log_exit('historyserver', self._hs_proc.poll())
      return False


    # Run a `hadoop job -list all'
    list_all = subprocess.Popen(
      (self._get_mapred_bin(env), 'job', '-list', 'all'),
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      env=env)

    ret = list_all.wait()
    if ret == 0:
      return True

    LOG.debug('MR2 not ready yet.\n%s\n%s' % (list_all.stderr.read(), list_all.stderr.read()))
    return False


  def _start_daemon(self, proc_name, conf_dir, env, hadoop_bin=None):
    if hadoop_bin is None:
      hadoop_bin = self._get_hadoop_bin(env)

    args = (hadoop_bin, '--config', conf_dir, proc_name)

    LOG.info('Starting Hadoop cluster daemon: %s' % (args,))
    stdout = file(self._logpath(proc_name + ".stdout"), 'w')
    stderr = file(self._logpath(proc_name + ".stderr"), 'w')

    return subprocess.Popen(args=args, stdout=stdout, stderr=stderr, env=env)

  def _get_hadoop_bin(self, env):
    try:
      return env['HADOOP_BIN']
    except KeyError:
      return os.path.join(get_run_root('ext/hadoop/hadoop'), 'bin', 'hadoop')

  def _get_mapred_bin(self, env):
    try:
      return env['MAPRED_BIN']
    except KeyError:
      return os.path.join(get_run_root('ext/hadoop/hadoop'), 'bin', 'mapred')

  def _get_yarn_bin(self, env):
    try:
      return env['YARN_BIN']
    except KeyError:
      return os.path.join(get_run_root('ext/hadoop/hadoop'), 'bin', 'yarn')

  def _get_hdfs_bin(self, env):
    try:
      return env['HDFS_BIN']
    except KeyError:
      return os.path.join(get_run_root('ext/hadoop/hadoop'), 'bin', 'hdfs')

  def _write_hdfs_site(self):
    self._dfs_http_port = find_unused_port()
    self._dfs_http_address = '%s:%s' % (self._fqdn, self._dfs_http_port)

    hdfs_configs = {
      'dfs.webhdfs.enabled': 'true',
      'dfs.http.address': self._dfs_http_address,
      'dfs.namenode.safemode.extension': 1,
      'dfs.namenode.safemode.threshold-pct': 0,
      'dfs.datanode.address': '%s:0' % self._fqdn,
      'dfs.datanode.http.address': '0.0.0.0:0', # Work around webhdfs redirect bug -- bind to all interfaces
      'dfs.datanode.ipc.address': '%s:0' % self._fqdn,
      'dfs.replication': 1,
      'dfs.safemode.min.datanodes': 1,
      'dfs.namenode.fs-limits.min-block-size': '1000',
      'dfs.permissions': 'true'
    }
    self._hdfs_site = self._tmppath('conf/hdfs-site.xml')
    write_config(hdfs_configs, self._hdfs_site)

  def _write_core_site(self):
    self._namenode_port = find_unused_port()
    self._fs_default_name = 'hdfs://%s:%s' % (self._fqdn, self._namenode_port,)

    core_configs = {
      'fs.default.name': self._fs_default_name,
      'hadoop.security.authorization': 'true',
      'hadoop.security.authentication': 'simple',
      'hadoop.proxyuser.hue.hosts': '*',
      'hadoop.proxyuser.hue.groups': '*',
      'hadoop.proxyuser.oozie.hosts': '*',
      'hadoop.proxyuser.oozie.groups': '*',
      'hadoop.proxyuser.%s.hosts' % (getpass.getuser(),): '*',
      'hadoop.proxyuser.%s.groups' % (getpass.getuser(),): '*',
      'hadoop.tmp.dir': self._tmppath('hadoop_tmp_dir'),
      'fs.trash.interval': 10
    }
    self._core_site = self._tmppath('conf/core-site.xml')
    write_config(core_configs, self._core_site)

  def _write_yarn_site(self):
    self._rm_resource_port = find_unused_port()
    self._rm_port = find_unused_port()
    self._rm_scheduler_port = find_unused_port()
    self._rm_admin_port = find_unused_port()
    self._rm_webapp_port = find_unused_port()
    self._nm_port = find_unused_port()
    self._nm_webapp_port = find_unused_port()

    yarn_configs = {
      'yarn.resourcemanager.resource-tracker.address': '%s:%s' % (self._fqdn, self._rm_resource_port,),
      'yarn.resourcemanager.address': '%s:%s' % (self._fqdn, self._rm_port,),
      'yarn.resourcemanager.scheduler.address': '%s:%s' % (self._fqdn, self._rm_scheduler_port,),
      'yarn.resourcemanager.scheduler.class': 'org.apache.hadoop.yarn.server.resourcemanager.scheduler.fair.FairScheduler',
      'yarn.resourcemanager.admin.address': '%s:%s' % (self._fqdn, self._rm_admin_port,),
      'yarn.resourcemanager.webapp.address': '%s:%s' % (self._fqdn, self._rm_webapp_port,),

      'yarn.log-aggregation-enable': 'true',
      'yarn.dispatcher.exit-on-error': 'true',

      'yarn.nodemanager.local-dirs': self._local_dir,
      'yarn.nodemanager.log-dirs': self._logpath('yarn-logs'),
      'yarn.nodemanager.remote-app-log-dir': '/var/log/hadoop-yarn/apps',
      'yarn.nodemanager.localizer.address' : '%s:%s' % (self._fqdn, self._nm_port,),
      'yarn.nodemanager.aux-services': 'mapreduce_shuffle',
      'yarn.nodemanager.aux-services.mapreduce.shuffle.class': 'org.apache.hadoop.mapred.ShuffleHandler',
      'yarn.nodemanager.webapp.address': '%s:%s' % (self._fqdn, self._nm_webapp_port,),

      'yarn.app.mapreduce.am.staging-dir': '/tmp/hadoop-yarn/staging',

      'yarn.application.classpath':
      '''$HADOOP_CONF_DIR,
        $HADOOP_COMMON_HOME/share/hadoop/common/*,$HADOOP_COMMON_HOME/share/hadoop/common/lib/*,
        $HADOOP_HDFS_HOME/share/hadoop/hdfs/*,$HADOOP_HDFS_HOME/share/hadoop/hdfs/lib/*,
        $HADOOP_MAPRED_HOME/share/hadoop/mapreduce/*,$HADOOP_MAPRED_HOME/share/hadoop/mapreduce/lib/*,
        $HADOOP_YARN_HOME/share/hadoop/yarn/*,$HADOOP_YARN_HOME/share/hadoop/yarn/lib/*''',
    }
    self._yarn_site = self._tmppath('conf/yarn-site.xml')
    write_config(yarn_configs, self._tmppath('conf/yarn-site.xml'))


  def _write_mapred_site(self):
    self._jh_port = find_unused_port()
    self._jh_web_port = find_unused_port()
    self._mr_shuffle_port = find_unused_port()

    mapred_configs = {
      'mapred.job.tracker': '%s:%s' % (self._fqdn, self._rm_port,),
      'mapreduce.framework.name': 'yarn',
      'mapreduce.jobhistory.address': '%s:%s' % (self._fqdn, self._jh_port,),
      'mapreduce.jobhistory.webapp.address': '%s:%s' % (self._fqdn, self._jh_web_port,),
      'mapreduce.task.tmp.dir': self._tmppath('tasks'),
      'mapreduce.shuffle.port': self._mr_shuffle_port,
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


def shared_cluster():
  global _shared_cluster

  if _shared_cluster is None:
    if is_live_cluster():
      cluster = LiveHdfs()
    else:
      cluster = PseudoHdfs4()
      atexit.register(cluster.stop)

      cluster.start()

      fqdn = socket.getfqdn()
      webhdfs_url = "http://%s:%s/webhdfs/v1" % (fqdn, cluster.dfs_http_port,)

      closers = [
        hadoop.conf.HDFS_CLUSTERS['default'].FS_DEFAULTFS.set_for_testing(cluster.fs_default_name),
        hadoop.conf.HDFS_CLUSTERS['default'].WEBHDFS_URL.set_for_testing(webhdfs_url),

        hadoop.conf.YARN_CLUSTERS['default'].HOST.set_for_testing(fqdn),
        hadoop.conf.YARN_CLUSTERS['default'].PORT.set_for_testing(cluster._rm_port),

        hadoop.conf.YARN_CLUSTERS['default'].RESOURCE_MANAGER_API_URL.set_for_testing('http://%s:%s' % (cluster._fqdn, cluster._rm_webapp_port,)),
        hadoop.conf.YARN_CLUSTERS['default'].PROXY_API_URL.set_for_testing('http://%s:%s' % (cluster._fqdn, cluster._rm_webapp_port,)),
        hadoop.conf.YARN_CLUSTERS['default'].HISTORY_SERVER_API_URL.set_for_testing('%s:%s' % (cluster._fqdn, cluster._jh_web_port,)),
      ]

      old_caches = clear_sys_caches()

      def restore_config():
        restore_sys_caches(old_caches)
        for x in closers:
          x()

      cluster.shutdown_hook = restore_config

    _shared_cluster = cluster

  return _shared_cluster



"""
Manual start from the Hue shell.

build/env/bin/hue shell
>

from hadoop import pseudo_hdfs4
pseudo_hdfs4.main()

>
exit() # To shutdown cleanly
"""
def main():
  logging.basicConfig(level=logging.DEBUG)

  cluster = PseudoHdfs4()
  cluster.start()

  print "%s running" % (cluster,)
  print "fs.default.name=%s" % (cluster.fs_default_name,)
  print "dfs.http.address=%s" % (cluster.dfs_http_address,)
  print "jobtracker.thrift.port=%s" % (cluster.jt_thrift_port,)
  print "mapred.job.tracker=%s" % (cluster.mapred_job_tracker,)

  from IPython.Shell import IPShellEmbed
  IPShellEmbed()()

  cluster.stop()

