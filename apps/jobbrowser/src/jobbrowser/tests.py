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

import time

from nose.tools import assert_true, assert_false, assert_equal
from nose.plugins.skip import SkipTest

from desktop.lib.django_test_util import make_logged_in_client
from hadoop import mini_cluster
from jobsub.models import JobDesign
from jobsub.tests import parse_out_id, watch_till_complete
from jobbrowser import models, views

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
  assert_equal("A Bbb Ccc", views.format_counter_name("A_BBB_CCC"))


def get_hadoop_job_id(jobsubd, jobsub_id, timeout_sec=60):
  handle = SubmissionHandle(id=jobsub_id)
  job_data = jobsubd.client.get_job_data(handle)

  start = time.time()
  while len(job_data.hadoop_job_ids) == 0:
    assert_true(time.time() - start < timeout_sec,
        "Timed out waiting for job to start")
    time.sleep(1)
    job_data = jobsubd.client.get_job_data(handle)

  return job_data.hadoop_job_ids[0]


class TestJobBrowserWithHadoop(object):
  """
  Tests for JobBrowser that requires Hadoop. Use the same mini_cluster and jobsubd.
  """
  requires_hadoop = True

  @classmethod
  def setup_class(cls):
    raise SkipTest
    client = make_logged_in_client('test')
    cluster = mini_cluster.shared_cluster(conf=True)
    jobsubd = in_process_jobsubd(cluster.config_dir)

    # Make home directory
    cluster.fs.setuser(cluster.superuser)
    if not cluster.fs.exists("/user/test"):
      cluster.fs.mkdir("/user/test")
    cluster.fs.chown("/user/test", "test", "test")

    if not cluster.fs.exists("/tmp"):
      cluster.fs.mkdir("/tmp")
    cluster.fs.chmod("/tmp", int('777', 8))

    cluster.fs.setuser("test")

    cls.cluster = cluster
    cls.client = client
    cls.jobsubd = jobsubd

  @classmethod
  def teardown_class(cls):
    cls.jobsubd.exit()
    cls.cluster.shutdown()

  def test_uncommon_views(self):
    """
    These views exist, but tend not to be ever called,
    because they're not in the normal UI.
    """
    # None of these should raise
    self.client.get("/jobbrowser/clusterstatus")
    self.client.get("/jobbrowser/queues")
    self.client.get("/jobbrowser/jobbrowser")

    # This is not tested.
    # assert_equal("{}", self.client.get("/jobbrowser/jobs/%s/setpriority?priority=HIGH" % hadoop_job_id).content)

  def test_failed_jobs(self):
    """
    Test jobs with genuine failure, not just killed
    """
    # Create design that will fail because the script file isn't there
    self.cluster.fs.mkdir("/user/test/jt-test_failed_jobs")
    response = self.client.post("/jobsub/new/streaming", dict(
          hadoop_properties='',
          inputformat_class_0='org.apache.hadoop.mapred.TextInputFormat',
          input='/user/test/jt-test_failed_jobs',
          mapper_cmd="python hogalabogus.py",
          name="bogus stream",
          num_reduce_tasks="1",
          outputformat_class_0='org.apache.hadoop.mapred.TextOutputFormat',
          output='/user/test/out_stream.tmp',
          reducer_cmd='python hogalabogus.py',
          save_submit='off',
          submit='Save',
    ))

    # Submit the job
    design_id = response.context["saved"]
    response = self.client.post("/jobsub/submit/%d" % design_id)
    watch_id = parse_out_id(response)
    response = watch_till_complete(self.client, watch_id, timeout_sec=120)
    job_id = Submission.objects.get(id=watch_id).submission_handle.id
    hadoop_job_id = get_hadoop_job_id(self.jobsubd, job_id)

    # The single job view should have the failed task table
    response = self.client.get('/jobbrowser/jobs/%s' % (hadoop_job_id,))
    html = response.content.lower()
    assert_true('failed task' in html)

    # Select only failed jobs (should be present)
    response = self.client.get('/jobbrowser/jobs/?state=failed')
    assert_true(hadoop_job_id in response.content)

    # Select only killed jobs (should be absent)
    response = self.client.get('/jobbrowser/jobs/?state=killed')
    assert_true(hadoop_job_id not in response.content)

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


  def test_new_jobs(self):
    """
    Submit jobs. Let them succeed or fail and view them.
    """
    # Install examples
    import jobsub.management.commands.jobsub_setup as jobsub_setup
    if not jobsub_setup.Command().has_been_setup():
      jobsub_setup.Command().handle()

    # Run the sleep example, since it doesn't require user home directory
    design_id = JobDesign.objects.get(name__contains="Example: Sleep").id
    response = self.client.post("/jobsub/submit/%d" % (design_id,), dict(
                                                            map_sleep_time_millis=1,
                                                            num_mappers=1,
                                                            num_reducers=1,
                                                            reduce_sleep_time_millis=1))
    watch_id = parse_out_id(response)
    response = watch_till_complete(self.client, watch_id)
    job_id = Submission.objects.get(id=watch_id).submission_handle.id
    hadoop_job_id = get_hadoop_job_id(self.jobsubd, job_id)

    # All jobs page
    response = self.client.get('/jobbrowser/jobs/')
    assert_true(hadoop_job_id.lstrip('job_') in response.content)

    # Single job page
    response = self.client.get('/jobbrowser/jobs/%s' % hadoop_job_id)

    # Check some counters for single job.
    counters = response.context['job'].counters
    counters_file_bytes_written = counters['FileSystemCounters']['counters']['FILE_BYTES_WRITTEN']
    assert_true(counters_file_bytes_written['map'] > 0)
    assert_true(counters_file_bytes_written['reduce'] > 0)
    assert_equal(counters_file_bytes_written['displayName'], 'FILE_BYTES_WRITTEN')
    assert_equal(counters_file_bytes_written['displayName'], 'FILE_BYTES_WRITTEN')

    # We can't just check the complete contents of the python map because the
    # SLOTS_MILLIS_* entries have a variable number of milliseconds from
    # run-to-run.
    assert_equal(response.context['job'].counters['org.apache.hadoop.mapred.JobInProgress$Counter']['counters']['TOTAL_LAUNCHED_MAPS']['total'], 1)
    assert_equal(response.context['job'].counters['org.apache.hadoop.mapred.JobInProgress$Counter']['counters']['TOTAL_LAUNCHED_REDUCES']['total'], 1)
    assert_equal(response.context['job'].counters['org.apache.hadoop.mapred.JobInProgress$Counter']['counters']['FALLOW_SLOTS_MILLIS_MAPS']['total'], 0)
    assert_equal(response.context['job'].counters['org.apache.hadoop.mapred.JobInProgress$Counter']['counters']['FALLOW_SLOTS_MILLIS_REDUCES']['total'], 0)
    assert_true(response.context['job'].counters['org.apache.hadoop.mapred.JobInProgress$Counter']['counters']['SLOTS_MILLIS_MAPS']['total'] > 0)
    assert_true(response.context['job'].counters['org.apache.hadoop.mapred.JobInProgress$Counter']['counters']['SLOTS_MILLIS_REDUCES']['total'] > 0)

    # Check conf keys made it
    assert_equal(response.context['job'].conf_keys['mapredReducerClass'],
                 'org.apache.hadoop.examples.SleepJob')

    # There should be 4 tasks for this job: cleanup, setup, map, reduce
    response = self.client.get('/jobbrowser/jobs/%s/tasks' % (hadoop_job_id,))
    assert_true('Showing 1 to 4 of 4 tasks' in response.content)
    # Select by tasktype
    response = self.client.get('/jobbrowser/jobs/%s/tasks?tasktype=reduce' % (hadoop_job_id,))
    assert_true('Showing 1 to 1 of 1 tasks' in response.content)
    # Select by taskstate
    response = self.client.get('/jobbrowser/jobs/%s/tasks?taskstate=succeeded' % (hadoop_job_id,))
    assert_true('Showing 1 to 4 of 4 tasks' in response.content)
    # Select by text
    response = self.client.get('/jobbrowser/jobs/%s/tasks?tasktext=clean' % (hadoop_job_id,))
    assert_true('Showing 1 to 1 of 1 tasks' in response.content)

    # Run another sleep job but kill it
    response = self.client.post("/jobsub/submit/%d" % (design_id,), dict(
                                                            map_sleep_time_millis=1,
                                                            num_mappers=2000,
                                                            num_reducers=2000,
                                                            reduce_sleep_time_millis=1))
    job_id = parse_out_id(response)
    hadoop_job_id = get_hadoop_job_id(self.jobsubd, job_id)

    client2 = make_logged_in_client('test_non_superuser', is_superuser=False)
    response = client2.post('/jobbrowser/jobs/%s/kill' % (hadoop_job_id,))
    assert_equal("Permission denied.  User test_non_superuser cannot delete user test's job.",
      response.context["error"])

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

    self.client.post('/jobbrowser/jobs/%s/kill' % (hadoop_job_id,))

    # It should say killed
    response = self.client.get('/jobbrowser/jobs/%s' % (hadoop_job_id,))
    html = response.content.lower()
    assert_true(hadoop_job_id in html)
    assert_true('killed' in html)
    # Exercise select by taskstate
    self.client.get('/jobbrowser/jobs/%s/tasks?taskstate=failed' % (hadoop_job_id,))
    self.client.get('/jobbrowser/jobs/%s/tasks?taskstate=pending' % (hadoop_job_id,))
    self.client.get('/jobbrowser/jobs/%s/tasks?taskstate=succeeded' % (hadoop_job_id,))
    self.client.get('/jobbrowser/jobs/%s/tasks?taskstate=running' % (hadoop_job_id,))
    self.client.get('/jobbrowser/jobs/%s/tasks?taskstate=killed' % (hadoop_job_id,))

    # Test single task page
    late_task_id = hadoop_job_id.replace('job', 'task') + '_r_001999'
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
    attempt_id = early_task_id.replace('task', 'attempt') + '_0'
    response = self.client.get('/jobbrowser/jobs/%s/tasks/%s/attempts/%s' %
                          (hadoop_job_id, early_task_id, attempt_id))
    assert_true('syslog' in response.content)

    # Test dock jobs
    response = self.client.get('/jobbrowser/dock_jobs/')
    assert_true('completed' in response.content)
    # TODO(atm): I'm pretty sure the following test only passes because of
    # failed jobs which are run in test_failed_jobs
    assert_true('failed' in response.content)
