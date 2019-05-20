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
import socket
import subprocess
import threading
import time

from nose.tools import assert_equal, assert_true, assert_false

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.paths import get_run_root
from desktop.lib.test_utils import grant_access
from hadoop import pseudo_hdfs4
from hadoop.mini_cluster import write_config
from hadoop.pseudo_hdfs4 import is_live_cluster

from liboozie.oozie_api import get_oozie
from liboozie.conf import OOZIE_URL
from oozie.conf import REMOTE_SAMPLE_DIR


_oozie_lock = threading.Lock()


LOG = logging.getLogger(__name__)


class OozieServerProvider(object):
  """
  Setup a Oozie server.
  """
  OOZIE_TEST_PORT = '18001'
  OOZIE_HOME = get_run_root('ext/oozie/oozie')

  requires_hadoop = True
  integration = True
  is_oozie_running = False

  @classmethod
  def setup_class(cls):
    cls.cluster = pseudo_hdfs4.shared_cluster()
    cls.oozie, callback = cls._get_shared_oozie_server()
    cls.shutdown = [callback]

  @classmethod
  def wait_until_completion(cls, oozie_jobid, timeout=600.0, step=5):
    job = cls.oozie.get_job(oozie_jobid)
    start = time.time()

    while job.is_running() and (time.time() - start) < timeout:
      time.sleep(step)
      LOG.info('Checking status of %s...' % oozie_jobid)
      job = cls.oozie.get_job(oozie_jobid)
      LOG.info('[%d] Status after %d: %s' % (time.time(), time.time() - start, job))

    logs = cls.oozie.get_job_log(oozie_jobid)

    if job.is_running():
      msg = "[%d] %s took more than %d to complete: %s" % (time.time(), oozie_jobid, timeout, logs)
      LOG.info(msg)
      raise Exception(msg)
    else:
      LOG.info('[%d] Job %s took %d: %s' % (time.time(), job.id, time.time() - start, logs))

    return job

  @classmethod
  def _setup_conf_dir(cls, cluster):
    original_oozie_conf_dir = '%s/conf' % OozieServerProvider.OOZIE_HOME
    shutil.copytree(original_oozie_conf_dir, cluster._tmppath('conf/oozie'))
    cls._write_oozie_site(cluster)

  @classmethod
  def _write_oozie_site(cls, cluster):
    oozie_configs = {
      'oozie.service.ProxyUserService.proxyuser.hue.hosts': '*',
      'oozie.service.ProxyUserService.proxyuser.hue.groups': '*',
      'oozie.service.HadoopAccessorService.hadoop.configurations': '*=%s' % cluster._tmppath('conf'),
      'oozie.db.schema.name': 'oozie',
      'oozie.data.dir': cluster._tmppath('oozie_tmp_dir'),
      'oozie.service.JPAService.create.db.schema': 'false',
      'oozie.service.JPAService.jdbc.driver': 'org.apache.derby.jdbc.EmbeddedDriver',
      'oozie.service.JPAService.jdbc.url': 'jdbc:derby:${oozie.data.dir}/${oozie.db.schema.name}-db;create=true',
      'oozie.service.JPAService.jdbc.username': 'sa',
      'oozie.service.JPAService.jdbc.password': '',
      'oozie.service.SchemaService.wf.ext.schemas': '''shell-action-0.1.xsd,shell-action-0.2.xsd,shell-action-0.3.xsd,email-action-0.1.xsd,hive-action-0.2.xsd,
            hive-action-0.3.xsd,hive-action-0.4.xsd,hive-action-0.5.xsd,sqoop-action-0.2.xsd,sqoop-action-0.3.xsd,
            sqoop-action-0.4.xsd,ssh-action-0.1.xsd,ssh-action-0.2.xsd,distcp-action-0.1.xsd,distcp-action-0.2.xsd,
            oozie-sla-0.1.xsd,oozie-sla-0.2.xsd,
            hive2-action-0.1.xsd,
            spark-action-0.1.xsd''',
      'oozie.service.ActionService.executor.ext.classes': '''org.apache.oozie.action.email.EmailActionExecutor,
            org.apache.oozie.action.hadoop.HiveActionExecutor,
            org.apache.oozie.action.hadoop.ShellActionExecutor,
            org.apache.oozie.action.hadoop.SqoopActionExecutor,
            org.apache.oozie.action.hadoop.DistcpActionExecutor,
            org.apache.oozie.action.hadoop.Hive2ActionExecutor,
            org.apache.oozie.action.ssh.SshActionExecutor,
            org.apache.oozie.action.oozie.SubWorkflowActionExecutor,
            org.apache.oozie.action.hadoop.SparkActionExecutor''',
      'oozie.service.coord.normal.default.timeout': 120
    }
    write_config(oozie_configs, cluster._tmppath('conf/oozie/oozie-site.xml'))

  @classmethod
  def _start_oozie(cls, cluster):
    """
    Start oozie process.
    """
    OozieServerProvider._setup_conf_dir(cluster)

    args = [OozieServerProvider.OOZIE_HOME + '/bin/oozied.sh', 'run']
    env = os.environ
    env['OOZIE_DATA'] = cluster._tmppath('oozie_tmp_dir')
    env['OOZIE_HTTP_PORT'] = OozieServerProvider.OOZIE_TEST_PORT
    conf_dir = os.path.join(cluster.log_dir, 'oozie')
    os.mkdir(conf_dir)
    env['OOZIE_LOG'] = conf_dir
    env['OOZIE_CONFIG'] = cluster._tmppath('conf/oozie')

    LOG.info("Executing %s, env %s, cwd %s" % (repr(args), repr(env), cluster._tmpdir))
    process = subprocess.Popen(args=args, env=env, cwd=cluster._tmpdir, stdin=subprocess.PIPE)
    return process

  @classmethod
  def _reset_oozie(cls, cluster):
    env = os.environ

    env['OOZIE_DATA'] = cluster._tmppath('oozie_tmp_dir')

    args = ['rm', '-r', '%s/data/oozie-db' % cluster._tmppath('oozie_tmp_dir')]
    LOG.info("Executing %s, env %s" % (args, env))
    subprocess.call(args, env=env)

    args = [OozieServerProvider.OOZIE_HOME + '/bin/ooziedb.sh',  'create', '-sqlfile', 'oozie.sql', '-run']
    LOG.info("Executing %s, env %s" % (args, env))
    subprocess.call(args, env=env)

  @classmethod
  def _setup_sharelib(cls):
    LOG.info("Copying Oozie sharelib")
    user_home = cls.cluster.fs.do_as_user(getpass.getuser(), cls.cluster.fs.get_home_dir)
    oozie_share_lib = user_home + '/share'
    cls.cluster.fs.do_as_user(getpass.getuser(), cls.cluster.fs.create_home_dir)

    env = os.environ
    args = [
        OozieServerProvider.OOZIE_HOME + '/bin/oozie-setup.sh',
        'sharelib',
        'create',
        '-fs',
        cls.cluster.fs.fs_defaultfs,
        '-locallib',
        OozieServerProvider.OOZIE_HOME + '/oozie-sharelib.tar.gz'
    ]
    LOG.info("Executing %s, env %s" % (args, env))
    subprocess.call(args, env=env)
    LOG.info("Oozie sharelib copied to %s" % oozie_share_lib)

  @classmethod
  def _get_shared_oozie_server(cls):
    callback = lambda: None

    _oozie_lock.acquire()

    try:
      if not OozieServerProvider.is_oozie_running:
        cluster = pseudo_hdfs4.shared_cluster()

        if is_live_cluster():
          def shutdown():
            pass
        else:
          LOG.info('\nStarting a Mini Oozie. Requires "tools/jenkins/jenkins.sh" to be previously ran.\n')
          LOG.info('See https://issues.cloudera.org/browse/HUE-861\n')

          finish = (
            OOZIE_URL.set_for_testing("http://%s:%s/oozie" % (socket.getfqdn(), OozieServerProvider.OOZIE_TEST_PORT)),
          )

          # Setup
          cls._setup_sharelib()
          cls._reset_oozie(cluster)

          p = cls._start_oozie(cluster)

          def kill():
            LOG.info("Killing Oozie server (pid %d)." % p.pid)
            os.kill(p.pid, 9)
            p.wait()
          atexit.register(kill)

          def shutdown():
            for f in finish:
              f()
            cluster.stop()

        start = time.time()
        started = False
        sleep = 0.01

        while not started and time.time() - start < 30.0:
          status = None
          try:
            LOG.info('Check Oozie status...')
            status = get_oozie(cluster.superuser).get_oozie_status()
            if status['systemMode'] == 'NORMAL':
              started = True
              break
            time.sleep(sleep)
            sleep *= 2
          except Exception, e:
            LOG.info('Oozie server status not NORMAL yet: %s - %s' % (status, e))
            time.sleep(sleep)
            sleep *= 2
            pass

        if not started:
          raise Exception("Oozie server took too long to come up.")

        OozieServerProvider.is_oozie_running = True
        callback = shutdown
    finally:
      _oozie_lock.release()

    cluster = pseudo_hdfs4.shared_cluster()
    return get_oozie(cluster.superuser), callback


class TestMiniOozie(OozieServerProvider):

  def test_oozie_status(self):
    user = getpass.getuser()

    assert_equal(get_oozie(user).get_oozie_status()['systemMode'], 'NORMAL')

    if is_live_cluster():
      assert_true(self.cluster.fs.exists('/user/oozie/share/lib'))
    else:
      assert_true(self.cluster.fs.exists('/user/%(user)s/share/lib' % {'user': user}))


class TestOozieWorkspace(object):
  requires_hadoop = True
  integration = True

  def setUp(self):
    self.cluster = pseudo_hdfs4.shared_cluster()
    self.cli = make_logged_in_client(username='admin', is_superuser=True)
    grant_access('admin', 'admin', 'filebrowser')
    self.cluster.fs.setuser('admin')

  def test_workspace_has_enough_permissions(self):
    reset = REMOTE_SAMPLE_DIR.set_for_testing('/tmp/oozie_test_workspace_has_enough_permissions')
    try:
      resp = self.cli.get('/desktop/debug/check_config')
      assert_false('The permissions of workspace' in resp.content, resp)

      self.cluster.fs.mkdir(REMOTE_SAMPLE_DIR.get())
      assert_equal(oct(040755), oct(self.cluster.fs.stats(REMOTE_SAMPLE_DIR.get())["mode"]))
      resp = self.cli.get('/desktop/debug/check_config')
      assert_true('The permissions of workspace' in resp.content, resp)

      permissions_dict = {
          'group_read': True, 'other_execute': True, 'user_write': True, 'user_execute': True,
          'sticky': False, 'user_read': True, 'other_read': True, 'other_write': True,
          'group_write': False, 'group_execute': True
      }

      kwargs = {'path': [REMOTE_SAMPLE_DIR.get()]}
      kwargs.update(permissions_dict)

      # Add write permission to Others
      response = self.cli.post("/filebrowser/chmod", kwargs)
      assert_equal(oct(040757), oct(self.cluster.fs.stats(REMOTE_SAMPLE_DIR.get())["mode"]))

      resp = self.cli.get('/desktop/debug/check_config')
      assert_false('The permissions of workspace' in resp.content, resp)

    finally:
      self.cluster.fs.rmdir(REMOTE_SAMPLE_DIR.get(), skip_trash=True)
      reset()
