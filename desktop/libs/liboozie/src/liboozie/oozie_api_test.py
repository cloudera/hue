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

import logging
import os
import time
import subprocess
import threading

from nose.plugins.skip import SkipTest
from nose.tools import assert_equal, assert_true

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.paths import get_run_root

from liboozie.oozie_api import get_oozie
from liboozie.conf import OOZIE_URL
from hadoop import pseudo_hdfs4


_oozie_running = False
_oozie_lock = threading.Lock()

LOG = logging.getLogger(__name__)

# TODO HUE-752
class OozieServerProvider(object):
  """
  Setup a Oozie server.
  """
  STATES_WF_COMPLETION = ('SUCCEEDED' , 'KILLED', 'FAILED')
  OOZIE_TEST_PORT = '18080'
  OOZIE_HOME = get_run_root('ext/oozie/oozie')

  requires_hadoop = True

  @classmethod
  def setup_class(cls):
    raise SkipTest

    cls.cluster = pseudo_hdfs4.shared_cluster()
    cls.client = make_logged_in_client()
    cls.oozie, callback = cls._get_shared_oozie_server()
    cls.shutdown = [ callback ]

  def wait_until_completion(self, jobid, timeout=60.0, step=1):
    sleep = 0
    workflow = None
    if step < 0:
      step = 1
    start = time.time()

    while not self.is_job_completed(workflow) and time.time() - start < timeout:
      time.sleep(sleep)
      sleep = sleep + step
      LOG.info('Checking status of %s...' % jobid)
      workflow = self.oozie.get_job(jobid)
    if not self.is_job_completed(workflow):
      logs = self.oozie.get_job_log(jobid)
      raise Exception("%s took too long to complete: %s" % (jobid, logs))

    return workflow

  def is_job_completed(self, workflow):
    # Only for Workflows so far
    if workflow is None:
      return False
    LOG.info(workflow.status)
    return workflow.status in OozieServerProvider.STATES_WF_COMPLETION

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
  def _get_shared_oozie_server(cls):
    global _oozie_running
    callback = lambda: None

    _oozie_lock.acquire()
    if not _oozie_running:
      finish = (
        OOZIE_URL.set_for_testing("http://localhost:%s/oozie" % OozieServerProvider.OOZIE_TEST_PORT),
      )

      cluster = pseudo_hdfs4.shared_cluster()

      start = time.time()
      started = False
      sleep = 0.01
      while not started and time.time() - start < 20.0:
        try:
          LOG.info('Check Oozie status...')
          status = get_oozie().get_oozie_status()
          if status['systemMode'] == 'NORMAL':
            started = True
            break
          time.sleep(sleep)
          sleep *= 2
        except:
          LOG.info('Oozie server status not NORMAL yet.')
          time.sleep(sleep)
          sleep *= 2
          pass
      if not started:
        raise Exception("Oozie server took too long to come up.")

      _oozie_running = True
      def shutdown():
        for f in finish:
          f()
        cluster.stop()
      callback = shutdown

    _oozie_lock.release()

    return get_oozie(), callback


class TestoozieWithHadoop(OozieServerProvider):
  def test_oozie_status(self):
    assert_equal(self.oozie.get_oozie_status()['systemMode'], 'NORMAL')

  def test_oozie_example(self):
    jobid = None

    try:
      self.cluster.fs.setuser('hue')
      self.cluster.fs.create_home_dir()
      home = self.cluster.fs.get_home_dir()

      self.cluster.put(OozieServerProvider + '/oozie/examples', home)
      self.cluster.put(OozieServerProvider + '/oozie/examples/input-data/text/data.txt', home)
      self.cluster.chmod(home, '0777')

      application_path = self.cluster._fs_default_name + home + '/examples/apps/map-reduce'
      assert_true(self.cluster.fs.exists(home + '/examples/apps/map-reduce'))

      jobid = self.oozie.submit_workflow(application_path, {
          'nameNode': self.cluster._fs_default_name,
          'jobTracker': self.cluster.mapred_job_tracker,
          'queueName': 'default',
          'examplesRoot': 'examples',
          'outputDir': 'test-out'})
      assert_true(jobid)

      self.oozie.job_control(jobid, 'start')
      workflow = self.wait_until_completion(jobid)

      assert_equal('SUCCEEDED', workflow.status)
      assert_true(self.cluster.fs.exists('output-data'))
    except:
      if jobid is not None:
        print self.oozie.get_job_log(jobid)
      raise
