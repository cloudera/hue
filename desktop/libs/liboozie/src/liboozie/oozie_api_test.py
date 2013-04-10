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
import socket
import subprocess
import threading
import time

from nose.tools import assert_equal, assert_true

from desktop.lib.paths import get_run_root
from hadoop import pseudo_hdfs4

from liboozie.oozie_api import get_oozie
from liboozie.conf import OOZIE_URL


_oozie_lock = threading.Lock()

LOG = logging.getLogger(__name__)


class OozieServerProvider(object):
  """
  Setup a Oozie server.
  """
  OOZIE_TEST_PORT = '18080'
  OOZIE_HOME = get_run_root('ext/oozie/oozie')

  requires_hadoop = True
  is_oozie_running = False

  @classmethod
  def setup_class(cls):
    cls.cluster = pseudo_hdfs4.shared_cluster()
    cls.oozie, callback = cls._get_shared_oozie_server()
    cls.shutdown = [callback]

  @classmethod
  def wait_until_completion(cls, oozie_jobid, timeout=300.0, step=5):
    job = cls.oozie.get_job(oozie_jobid)
    start = time.time()

    while job.is_running() and time.time() - start < timeout:
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
  def _start_oozie(cls, cluster):
    """
    Start oozie process.
    """
    args = [OozieServerProvider.OOZIE_HOME + '/bin/oozied.sh', 'run']
    env = os.environ
    env['OOZIE_HTTP_PORT'] = OozieServerProvider.OOZIE_TEST_PORT
    conf_dir = os.path.join(cluster.log_dir, 'oozie')
    os.mkdir(conf_dir)
    env['OOZIE_LOG'] = conf_dir

    LOG.info("Executing %s, env %s, cwd %s" % (repr(args), repr(env), cluster._tmpdir))
    process = subprocess.Popen(args=args, env=env, cwd=cluster._tmpdir, stdin=subprocess.PIPE)
    return process

  @classmethod
  def _reset_oozie(cls):
    env = os.environ

    args = ['rm', '-r', OozieServerProvider.OOZIE_HOME + '/data/oozie-db']
    LOG.info("Executing %s, env %s" % (args, env))
    subprocess.call(args, env=env)

    args = [OozieServerProvider.OOZIE_HOME + '/bin/ooziedb.sh',  'create', '-sqlfile', 'oozie.sql', '-run']
    LOG.info("Executing %s, env %s" % (args, env))
    subprocess.call(args, env=env)

  @classmethod
  def _setup_sharelib(cls):
    # At some point could reuse:
    # oozie-setup.sh sharelib create -fs FS_URI
    LOG.info("Copying Oozie sharelib")
    user_home = cls.cluster.fs.do_as_user(getpass.getuser(), cls.cluster.fs.get_home_dir)
    oozie_share_lib = user_home + '/share'
    cls.cluster.fs.do_as_user(getpass.getuser(), cls.cluster.fs.create_home_dir)
    cls.cluster.fs.do_as_user(getpass.getuser(), cls.cluster.fs.copyFromLocal, OozieServerProvider.OOZIE_HOME + '/share', oozie_share_lib)
    LOG.info("Oozie sharelib copied to %s" % oozie_share_lib)

  @classmethod
  def _get_shared_oozie_server(cls):
    callback = lambda: None

    _oozie_lock.acquire()

    if not OozieServerProvider.is_oozie_running:
      LOG.info('\nStarting a Mini Oozie. Requires "tools/jenkins/jenkins.sh" to be previously ran.\n')
      LOG.info('See https://issues.cloudera.org/browse/HUE-861\n')

      finish = (
        OOZIE_URL.set_for_testing("http://%s:%s/oozie" % (socket.getfqdn(), OozieServerProvider.OOZIE_TEST_PORT)),
      )

      # Setup
      cluster = pseudo_hdfs4.shared_cluster()
      cls._setup_sharelib()
      cls._reset_oozie()

      p = cls._start_oozie(cluster)

      def kill():
        LOG.info("Killing Oozie server (pid %d)." % p.pid)
        os.kill(p.pid, 9)
        p.wait()
      atexit.register(kill)

      start = time.time()
      started = False
      sleep = 0.01

      while not started and time.time() - start < 30.0:
        status = None
        try:
          LOG.info('Check Oozie status...')
          status = get_oozie().get_oozie_status()
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

      def shutdown():
        for f in finish:
          f()
        cluster.stop()
      callback = shutdown

    _oozie_lock.release()

    return get_oozie(), callback


class TestMiniOozie(OozieServerProvider):

  def test_oozie_status(self):
    assert_equal(get_oozie().get_oozie_status()['systemMode'], 'NORMAL')

    assert_true(self.cluster.fs.exists('/user/%(user)s/share/lib' % {'user': getpass.getuser()}))
