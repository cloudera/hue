
import atexit
import logging
import pwd
import os
import shutil
import signal
import subprocess
import tempfile
import textwrap
import time

import desktop
import hadoop
from hadoop.mini_cluster import find_unused_port, write_config

# Shared global HDFS (for CDH4).
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
  """This class runs HDFS (CDH4) locally, in pseudo-distributed mode"""

  def __init__(self):
    self._tmpdir = tempfile.mkdtemp(prefix='tmp_hue_')
    self._superuser = pwd.getpwuid(os.getuid()).pw_name
    self._fs = None

    self._log_dir = None
    self._dfs_http_port = None
    self._dfs_http_address = None
    self._namenode_port = None
    self._fs_default_name = None

    self._nn_proc = None
    self._dn_proc = None

    self.shutdown_hook = None

  def __str__(self):
    return "PseudoHdfs4 (%s) at %s" % (self._fs_default_name, self._tmpdir)

  @property
  def superuser(self):
    return self._superuser

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
  def fs(self):
    if self._fs is None:
      if self._dfs_http_address is None:
        LOG.warn("Attempt to access uninitialized filesystem")
        return None
      self._fs = hadoop.fs.webhdfs.WebHdfs(
        "http://%s/webhdfs/v1" % (self._dfs_http_address,))
    return self._fs

  def stop(self):
    """Kills the cluster ungracefully."""
    while self._nn_proc is not None and self._nn_proc.poll() is None:
      os.kill(self._nn_proc.pid, signal.SIGKILL)
      LOG.info('Stopping NameNode pid %s' % (self._nn_proc.pid,))
      time.sleep(0.5)

    while self._dn_proc is not None and self._dn_proc.poll() is None:
      os.kill(self._dn_proc.pid, signal.SIGKILL)
      LOG.info('Stopping DataNode pid %s' % (self._dn_proc.pid,))
      time.sleep(0.5)

    self._nn_proc = None
    self._dn_proc = None

    if CLEANUP_TMP_DIR == 'false':
      LOG.info('Skipping cleanup of temp directory "%s"' % (self._tmpdir,))
    else:
      LOG.info('Cleaning up temp directory "%s". '
               'Use $MINI_CLUSTER_CLEANUP to avoid.' % (self._tmpdir,))
      shutil.rmtree(self._tmpdir)

    if self.shutdown_hook is not None:
      self.shutdown_hook()


  def _tmppath(self, filename):
    """Return a filepath inside temp dir"""
    return os.path.join(self._tmpdir, filename)

  def _logpath(self, filename):
    """Return a filepath inside log dir"""
    return os.path.join(self._log_dir, filename)

  def start(self):
    LOG.info("Using temporary directory: %s" % (self._tmpdir,))

    # Fix up superuser group mapping
    if self.superuser not in TEST_USER_GROUP_MAPPING:
      TEST_USER_GROUP_MAPPING[self.superuser] = [self.superuser]

    # This is where we prepare our Hadoop configuration
    conf_dir = self._tmppath('conf')
    os.mkdir(conf_dir)

    self._log_dir = self._tmppath('logs')
    os.mkdir(self._log_dir)

    # Write out the Hadoop conf files
    self._write_hadoop_metrics_conf(conf_dir)
    self._write_core_site()
    self._write_hdfs_site()

    # More stuff to setup in the environment
    env = dict(
      HADOOP_CONF_DIR = conf_dir,
      HADOOP_HEAPSIZE = "128",
      HADOOP_LOG_DIR = self._log_dir,
      USER = self.superuser,
      LANG = "en_US.UTF-8",
      PATH = os.environ['PATH'],
    )

    if "JAVA_HOME" in os.environ:
      env['JAVA_HOME'] = os.environ['JAVA_HOME']

    LOG.debug("Environment:\n" + "\n".join([ str(x) for x in sorted(env.items()) ]))

    # Format HDFS
    self._format(conf_dir, env)

    # Run them
    self._nn_proc = self._start_daemon('namenode', conf_dir, env)
    self._dn_proc = self._start_daemon('datanode', conf_dir, env)

    # Make sure they're running
    deadline = time.time() + STARTUP_DEADLINE
    while not self._is_ready():
      if time.time() > deadline:
        self.stop()
        raise RuntimeError('%s is taking too long to start' % (self,))
      time.sleep(5)

  def _format(self, conf_dir, env):
    args = (hadoop.conf.HADOOP_BIN.get(), 
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


  def _is_ready(self):
    def log_exit(exit_code, proc_name):
      LOG.info('%s exited with %s' % (proc_name, exit_code))
      LOG.debug('--------------------- STDOUT:\n' +
                file(self._logpath(proc_name + '.stdout')))
      LOG.debug('--------------------- STDERR:\n' +
                file(self._logpath(proc_name + '.stderr')))

    if self._nn_proc.poll() is not None:
      log_exit('namenode', self._nn_proc.poll())
      return False
    if self._dn_proc.poll() is not None:
      log_exit('datanode', self._dn_proc.poll())
      return False

    # Run a `dfsadmin -report' against it
    dfsreport = subprocess.Popen(
      (hadoop.conf.HADOOP_BIN.get(),
       'dfsadmin',
       '-Dfs.default.name=%s' % self._fs_default_name,
       '-report'),
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE)

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


  def _start_daemon(self, proc_name, conf_dir, env):
    """Start a hadoop daemon. Returns the Popen object."""
    args = (hadoop.conf.HADOOP_BIN.get(), 
            '--config', conf_dir,
            proc_name)
    LOG.info('Starting pseudo HDFS4 cluster: %s' % (args,))
    stdout = file(self._logpath(proc_name + ".stdout"), 'w')
    stderr = file(self._logpath(proc_name + ".stderr"), 'w')

    return subprocess.Popen(
      args=args,
      stdout=stdout,
      stderr=stderr,
      env=env)

  def _write_hdfs_site(self):
    self._dfs_http_port = find_unused_port()
    self._dfs_http_address = 'localhost:%s' % (self._dfs_http_port,)

    hdfs_configs = {
      'dfs.webhdfs.enabled': 'true',
      'dfs.http.address': self._dfs_http_address,
      'dfs.namenode.safemode.extension': 1,
      'dfs.namenode.safemode.threshold-pct': 0,
      'dfs.replication': 1,
      'dfs.safemode.min.datanodes': 1,
    }
    write_config(hdfs_configs, self._tmppath('conf/hdfs-site.xml'))

  def _write_core_site(self):
    # Prep user group mapping file
    ugm_properties = self._tmppath('ugm.properties')
    self._write_static_group_mapping(ugm_properties)
    self._namenode_port = find_unused_port()
    self._fs_default_name = 'hdfs://localhost:%s' % (self._namenode_port,)

    core_configs = {
      'fs.default.name': self._fs_default_name,
      'hadoop.security.authorization': 'true',
      'hadoop.security.authentication': 'simple',
      'hadoop.proxyuser.%s.groups' % (self.superuser,): 'users,supergroup',
      'hadoop.proxyuser.%s.hosts' % (self.superuser,): 'localhost',
      'hadoop.tmp.dir': self._tmppath('hadoop_tmp_dir'),
    }
    write_config(core_configs, self._tmppath('conf/core-site.xml'))

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
    cluster.start()

    # Fix config to reflect the cluster setup.
    closers = [
      hadoop.conf.HDFS_CLUSTERS['default'].NN_HOST.set_for_testing('localhost'),
      hadoop.conf.HDFS_CLUSTERS['default'].NN_HTTP_PORT.set_for_testing(cluster.dfs_http_port),
      hadoop.conf.HDFS_CLUSTERS['default'].NN_HDFS_PORT.set_for_testing(cluster.namenode_port),
    ]

    desktop.lib.fsmanager.reset()
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

  from IPython.Shell import IPShellEmbed
  IPShellEmbed()()
  cluster.stop()
