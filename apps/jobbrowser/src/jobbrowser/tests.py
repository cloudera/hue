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

try:
    import json
except ImportError:
    import simplejson as json
import logging
import time
import unittest

from nose.tools import assert_true, assert_false, assert_equal

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access
from jobsub.models import OozieDesign
from liboozie.oozie_api_test import OozieServerProvider

from jobbrowser import models, views
from jobbrowser.conf import SHARE_JOBS


LOG = logging.getLogger(__name__)


def test_dots_to_camel_case():
  assert_equal("fooBar", models.dots_to_camel_case("foo.bar"))
  assert_equal("fooBarBaz", models.dots_to_camel_case("foo.bar.baz"))
  assert_equal("foo", models.dots_to_camel_case("foo"))
  assert_equal("foo.", models.dots_to_camel_case("foo."))

def test_get_path():
  assert_equal("/foo/bar", models.get_path("hdfs://host/foo/bar"))

def test_format_counter_name():
  assert_equal("Foo Bar", views.format_counter_name("fooBar"))
  assert_equal("Foo Bar Baz", views.format_counter_name("fooBarBaz"))
  assert_equal("Foo", views.format_counter_name("foo"))
  assert_equal("Foo.", views.format_counter_name("foo."))
  assert_equal("A Bbb Ccc", views.format_counter_name("A_BBB_CCC"))\

def get_hadoop_job_id(oozie_api, oozie_jobid, action_index=1, timeout=60, step=5):
  hadoop_job_id = None
  start = time.time()
  while not hadoop_job_id and time.time() - start < timeout:
    time.sleep(step)
    hadoop_job_id = oozie_api.get_job(oozie_jobid).actions[action_index].externalId
  if not hadoop_job_id:
    logs = OozieServerProvider.oozie.get_job_log(oozie_jobid)
    msg = "[%d] %s took more than %d to create a job: %s" % (time.time(), oozie_jobid, timeout, logs)
    LOG.info(msg)
    raise Exception(msg)
  return hadoop_job_id


class TestJobBrowserWithHadoop(unittest.TestCase, OozieServerProvider):
  """
  Tests for JobBrowser that requires Hadoop. Use the same mini_cluster and jobsubd.
  """
  requires_hadoop = True
  user_count = 0

  @classmethod
  def setup_class(cls):
    OozieServerProvider.setup_class()
    if not cls.cluster.fs.exists("/tmp"):
      cls.cluster.fs.do_as_superuser(cls.cluster.fs.mkdir, "/tmp")
    cls.cluster.fs.do_as_superuser(cls.cluster.fs.chmod, "/tmp", 0777)

    # Install examples
    import jobsub.management.commands.jobsub_setup as jobsub_setup
    if not jobsub_setup.Command().has_been_setup():
      jobsub_setup.Command().handle()

    cls.sleep_design_id = OozieDesign.objects.get(name='sleep_job').id

  def setUp(self):
    TestJobBrowserWithHadoop.user_count += 1
    self.username = 'test' + str(TestJobBrowserWithHadoop.user_count)
    self.home_dir = '/user/%s' % self.username

    self.cluster.fs.do_as_user(self.username, self.cluster.fs.create_home_dir, self.home_dir)
    self.cluster.fs.do_as_superuser(self.cluster.fs.chmod, self.home_dir, 0777, True)
    self.cluster.fs.do_as_superuser(self.cluster.fs.chown, self.home_dir, self.username, "test", recursive=True)

    self.client = make_logged_in_client(username=self.username, is_superuser=False, groupname='test')
    grant_access(self.username, 'test', 'jobsub')
    grant_access(self.username, 'test', 'jobbrowser')

    # Ensure access to MR folder
    self.cluster.fs.do_as_superuser(self.cluster.fs.chmod, '/tmp', 0777, recursive=True)

    self.cluster.fs.setuser(self.username)

  def tearDown(self):
    try:
      # Remove user home directories.
      self.cluster.fs.do_as_superuser(self.cluster.fs.rmtree, self.home_dir)
    except:
      pass

  def test_uncommon_views(self):
    """
    These views exist, but tend not to be ever called,
    because they're not in the normal UI.
    """
    # None of these should raise
    self.client.get("/jobbrowser/clusterstatus")
    self.client.get("/jobbrowser/queues")
    self.client.get("/jobbrowser/jobbrowser")

  def test_failed_jobs(self):
    """
    Test jobs with genuine failure, not just killed
    """
    # Create design that will fail because the script file isn't there
    INPUT_DIR = self.home_dir + '/input'
    OUTPUT_DIR = self.home_dir + '/output'
    try:
        self.cluster.fs.mkdir(self.home_dir + "/jt-test_failed_jobs")
        self.cluster.fs.mkdir(INPUT_DIR)
        self.cluster.fs.rmtree(OUTPUT_DIR)
    except:
        # rmtree probably failed here.
        pass
    response = self.client.post('/jobsub/new_design/mapreduce', {
        'wf-name': ['test_failed_jobs-1'],
        'wf-description': ['description test_failed_jobs-1'],
        'action-args': [''],
        'action-jar_path': ['/user/hue/jobsub/examples/hadoop-examples.jar'],
        'action-archives': ['[]'],
        'action-job_properties': ['[{"name":"mapred.input.dir","value":"%s"},\
            {"name":"mapred.output.dir","value":"%s"},\
            {"name":"mapred.mapper.class","value":"org.apache.hadoop.mapred.lib.dne"},\
            {"name":"mapred.combiner.class","value":"org.apache.hadoop.mapred.lib.dne"},\
            {"name":"mapred.reducer.class","value":"org.apache.hadoop.mapred.lib.dne"}]' % (INPUT_DIR, OUTPUT_DIR)],
        'action-files': ['[]']}, follow=True)
    designs = json.loads(response.context['designs'])

    # Submit the job
    design_id = designs[0]['id']
    response = self.client.post("/jobsub/submit_design/%d" % design_id, follow=True)
    oozie_jobid = response.context['jobid']
    job = OozieServerProvider.wait_until_completion(oozie_jobid, timeout=500, step=1)
    hadoop_job_id = get_hadoop_job_id(self.oozie, oozie_jobid, 1)

    # Select only killed jobs (should be absent)
    # Taking advantage of the fact new jobs are at the top of the list!
    response = self.client.get('/jobbrowser/jobs/?state=killed')
    assert_false(hadoop_job_id in response.content)

    # Select only failed jobs (should be present)
    # Map job should succeed. Reduce job should fail.
    response = self.client.get('/jobbrowser/jobs/?state=failed')
    assert_true(hadoop_job_id in response.content)

    # The single job view should have the failed task table
    response = self.client.get('/jobbrowser/jobs/%s' % (hadoop_job_id,))
    html = response.content.lower()
    assert_true('failed task' in html)

    # The map task should say success (empty input)
    map_task_id = hadoop_job_id.replace('job', 'task') + '_m_000000'
    response = self.client.get('/jobbrowser/jobs/%s/tasks/%s' % (hadoop_job_id, map_task_id))
    assert_true('succeed' in response.content)
    assert_true('failed' not in response.content)

    # The reduce task should say failed
    reduce_task_id = hadoop_job_id.replace('job', 'task') + '_r_000000'
    response = self.client.get('/jobbrowser/jobs/%s/tasks/%s' % (hadoop_job_id, reduce_task_id))
    assert_true('succeed' not in response.content)
    assert_true('failed' in response.content)

    # Selecting by failed state should include the failed map
    response = self.client.get('/jobbrowser/jobs/%s/tasks?taskstate=failed' % (hadoop_job_id,))
    assert_true('_r_000000' in response.content)
    assert_true('_m_000000' not in response.content)

  def test_kill_job(self):
    """
    Test job in kill state.
    """
    # Clone design
    assert_equal(0, OozieDesign.objects.filter(owner__username=self.username).count())
    self.client.post('/jobsub/clone_design/%d' % self.sleep_design_id)
    assert_equal(1, OozieDesign.objects.filter(owner__username=self.username).count())

    # Run the sleep example, since it doesn't require user home directory
    design_id = OozieDesign.objects.get(owner__username=self.username).id
    response = self.client.post("/jobsub/submit_design/%d" % (design_id,),
      dict(map_sleep_time=1,
           num_maps=1,
           num_reduces=1,
           reduce_sleep_time=1),
      follow=True)
    oozie_jobid = response.context['jobid']

    # Wait for a job to be created and fetch job ID
    hadoop_job_id = get_hadoop_job_id(self.oozie, oozie_jobid, 1)

    client2 = make_logged_in_client('test_non_superuser', is_superuser=False, groupname='test')
    grant_access('test_non_superuser', 'test', 'jobbrowser')
    response = client2.post('/jobbrowser/jobs/%s/kill' % (hadoop_job_id,))
    assert_equal("Permission denied.  User test_non_superuser cannot delete user %s's job." % self.username, response.context["error"])

    # Make sure that the first map task succeeds before moving on
    # This will keep us from hitting timing-related failures
    first_mapper = hadoop_job_id.replace('job', 'task') + '_m_000000'
    start = time.time()
    timeout_sec = 60
    while first_mapper not in \
        self.client.get('/jobbrowser/jobs/%s/tasks?taskstate=succeeded' % (hadoop_job_id,)).content:
      time.sleep(1)
      # If this assert fails, something has probably really failed
      assert_true(time.time() - start < timeout_sec,
          "Timed out waiting for first mapper to complete")

    # Kill task
    self.client.post('/jobbrowser/jobs/%s/kill' % (hadoop_job_id,))

    # It should say killed
    response = self.client.get('/jobbrowser/jobs/%s' % (hadoop_job_id,))
    html = response.content.lower()
    assert_true(hadoop_job_id in html)
    assert_true('killed' in html)

    # Exercise select by taskstate
    self.client.get('/jobbrowser/jobs/%s/tasks?taskstate=failed' % (hadoop_job_id,))
    self.client.get('/jobbrowser/jobs/%s/tasks?taskstate=succeeded' % (hadoop_job_id,))
    self.client.get('/jobbrowser/jobs/%s/tasks?taskstate=running' % (hadoop_job_id,))
    self.client.get('/jobbrowser/jobs/%s/tasks?taskstate=killed' % (hadoop_job_id,))

    # Test single task page
    late_task_id = hadoop_job_id.replace('job', 'task') + '_r_000000'
    response = self.client.get('/jobbrowser/jobs/%s/tasks/%s' % (hadoop_job_id, late_task_id))
    assert_false('succeed' in response.content)
    assert_true('killed' in response.content)

    # The first task should've succeeded
    # We use a different method of checking success for this one
    early_task_id = hadoop_job_id.replace('job', 'task') + '_m_000000'
    response = self.client.get('/jobbrowser/jobs/%s/tasks/%s' % (hadoop_job_id, early_task_id))
    assert_true('succeed' in response.content)
    assert_false('failed' in response.content)

    # Test single attempt page
    early_task_id = hadoop_job_id.replace('job', 'task') + '_m_000000'
    attempt_id = early_task_id.replace('task', 'attempt') + '_0'
    response = self.client.get('/jobbrowser/jobs/%s/tasks/%s/attempts/%s/logs' %
                          (hadoop_job_id, early_task_id, attempt_id))
    assert_true('syslog' in response.content)

    # Test dock jobs
    response = self.client.get('/jobbrowser/dock_jobs/')
    assert_false('completed' in response.content)
    assert_false('failed' in response.content)

  def test_job(self):
    """
    Test new job views.

    The status of the jobs should be the same as the status reported back by oozie.
    In this case, all jobs should succeed.
    """
    # Clone design
    assert_equal(0, OozieDesign.objects.filter(owner__username=self.username).count())
    self.client.post('/jobsub/clone_design/%d' % self.sleep_design_id)
    assert_equal(1, OozieDesign.objects.filter(owner__username=self.username).count())

    # Run the sleep example, since it doesn't require user home directory
    design_id = OozieDesign.objects.get(owner__username=self.username).id
    response = self.client.post("/jobsub/submit_design/%d" % (design_id,),
      dict(map_sleep_time=1,
           num_maps=1,
           num_reduces=1,
           reduce_sleep_time=1),
      follow=True)
    oozie_jobid = response.context['jobid']
    job = OozieServerProvider.wait_until_completion(oozie_jobid, timeout=120, step=1)
    hadoop_job_id = get_hadoop_job_id(self.oozie, oozie_jobid, 1)

    # All jobs page and fetch job ID
    # Taking advantage of the fact new jobs are at the top of the list!
    response = self.client.get('/jobbrowser/jobs/')
    assert_true(hadoop_job_id in response.content)

    # Make sure job succeeded
    response = self.client.get('/jobbrowser/jobs/?state=completed')
    assert_true(hadoop_job_id in response.content)
    response = self.client.get('/jobbrowser/jobs/?state=failed')
    assert_false(hadoop_job_id in response.content)
    response = self.client.get('/jobbrowser/jobs/?state=running')
    assert_false(hadoop_job_id in response.content)
    response = self.client.get('/jobbrowser/jobs/?state=killed')
    assert_false(hadoop_job_id in response.content)

    # Check sharing permissions
    # Login as ourself
    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = self.client.get('/jobbrowser/jobs/?user=')
      assert_true(hadoop_job_id in response.content)
    finally:
      finish()

    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = self.client.get('/jobbrowser/jobs/?user=')
      assert_true(hadoop_job_id in response.content)
    finally:
      finish()

    # Login as someone else
    client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test')
    grant_access("not_me", "test", "jobbrowser")

    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = client_not_me.get('/jobbrowser/jobs/?user=')
      assert_true(hadoop_job_id in response.content)
    finally:
      finish()

    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.get('/jobbrowser/jobs/?user=')
      assert_false(hadoop_job_id in response.content)
    finally:
      finish()

    # Single job page
    response = self.client.get('/jobbrowser/jobs/%s' % hadoop_job_id)

    # Check some counters for single job.
    counters = response.context['job'].counters
    counters_file_bytes_written = counters['org.apache.hadoop.mapreduce.FileSystemCounter']['counters']['FILE_BYTES_WRITTEN']
    assert_true(counters_file_bytes_written['map'] > 0)
    assert_true(counters_file_bytes_written['reduce'] > 0)

    # We can't just check the complete contents of the python map because the
    # SLOTS_MILLIS_* entries have a variable number of milliseconds from
    # run-to-run.
    assert_equal(response.context['job'].counters['org.apache.hadoop.mapreduce.JobCounter']['counters']['TOTAL_LAUNCHED_MAPS']['total'], 1)
    assert_equal(response.context['job'].counters['org.apache.hadoop.mapreduce.JobCounter']['counters']['TOTAL_LAUNCHED_REDUCES']['total'], 1)
    assert_equal(response.context['job'].counters['org.apache.hadoop.mapreduce.JobCounter']['counters']['FALLOW_SLOTS_MILLIS_MAPS']['total'], 0)
    assert_equal(response.context['job'].counters['org.apache.hadoop.mapreduce.JobCounter']['counters']['FALLOW_SLOTS_MILLIS_REDUCES']['total'], 0)
    assert_true(response.context['job'].counters['org.apache.hadoop.mapreduce.JobCounter']['counters']['SLOTS_MILLIS_MAPS']['total'] > 0)
    assert_true(response.context['job'].counters['org.apache.hadoop.mapreduce.JobCounter']['counters']['SLOTS_MILLIS_REDUCES']['total'] > 0)

    # There should be 4 tasks for this job: cleanup, setup, map, reduce
    response = self.client.get('/jobbrowser/jobs/%s/tasks' % (hadoop_job_id,))
    assert_true(len(response.context['page'].object_list), 4)
    # Select by tasktype
    response = self.client.get('/jobbrowser/jobs/%s/tasks?tasktype=reduce' % (hadoop_job_id,))
    assert_true(len(response.context['page'].object_list), 1)
    # Select by taskstate
    response = self.client.get('/jobbrowser/jobs/%s/tasks?taskstate=succeeded' % (hadoop_job_id,))
    assert_true(len(response.context['page'].object_list), 4)
    # Select by text
    response = self.client.get('/jobbrowser/jobs/%s/tasks?tasktext=clean' % (hadoop_job_id,))
    assert_true(len(response.context['page'].object_list), 1)

    # Test job single logs page
    response = self.client.get('/jobbrowser/jobs/%s/single_logs' % (hadoop_job_id))
    assert_true('syslog' in response.content)
