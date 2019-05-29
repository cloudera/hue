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


import json
import logging
import re
import time
import unittest

from django.contrib.auth.models import User
from django.urls import reverse
from nose.plugins.skip import SkipTest
from nose.tools import assert_true, assert_false, assert_equal, assert_raises

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access, add_to_group
from desktop.models import Document
from hadoop import cluster
from hadoop.conf import YARN_CLUSTERS
from hadoop.pseudo_hdfs4 import is_live_cluster
from hadoop.yarn import resource_manager_api, mapreduce_api, history_server_api, spark_history_server_api
from hadoop.yarn.spark_history_server_api import SparkHistoryServerApi
from liboozie.oozie_api_tests import OozieServerProvider
from oozie.models import Workflow

from jobbrowser import views
from jobbrowser.api import get_api
from jobbrowser.apis.query_api import QueryApi
from jobbrowser.apis import job_api
from jobbrowser.conf import SHARE_JOBS
from jobbrowser.models import can_view_job, can_modify_job, LinkJobLogs
from jobbrowser.yarn_models import SparkJob


LOG = logging.getLogger(__name__)
_INITIALIZED = False


class TestBrowser():

  def test_format_counter_name(self):
    assert_equal("Foo Bar", views.format_counter_name("fooBar"))
    assert_equal("Foo Bar Baz", views.format_counter_name("fooBarBaz"))
    assert_equal("Foo", views.format_counter_name("foo"))
    assert_equal("Foo.", views.format_counter_name("foo."))
    assert_equal("A Bbb Ccc", views.format_counter_name("A_BBB_CCC"))

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
  requires_hadoop = True
  integration = True

  @classmethod
  def setup_class(cls):
    OozieServerProvider.setup_class()

    cls.username = 'hue_jobbrowser_test'
    cls.home_dir = '/user/%s' % cls.username
    cls.cluster.fs.do_as_user(cls.username, cls.cluster.fs.create_home_dir, cls.home_dir)

    cls.client = make_logged_in_client(username=cls.username, is_superuser=False, groupname='test')
    cls.user = User.objects.get(username=cls.username)
    grant_access(cls.username, 'test', 'jobsub')
    grant_access(cls.username, 'test', 'jobbrowser')
    grant_access(cls.username, 'test', 'oozie')
    add_to_group(cls.username)

    cls.prev_user = cls.cluster.fs.user
    cls.cluster.fs.setuser(cls.username)

    cls.install_examples()
    cls.design = cls.create_design()

    # Run the sleep example, since it doesn't require user home directory
    design_id = cls.design.id
    response = cls.client.post(reverse('oozie:submit_workflow',
                                args=[design_id]),
                                data={u'form-MAX_NUM_FORMS': [u''],
                                      u'form-INITIAL_FORMS': [u'1'],
                                      u'form-0-name': [u'REDUCER_SLEEP_TIME'],
                                      u'form-0-value': [u'1'],
                                      u'form-TOTAL_FORMS': [u'1']},
                                follow=True)
    oozie_jobid = response.context[0]['oozie_workflow'].id
    OozieServerProvider.wait_until_completion(oozie_jobid)

    cls.hadoop_job_id = get_hadoop_job_id(cls.oozie, oozie_jobid, 1)
    cls.hadoop_job_id_short = views.get_shorter_id(cls.hadoop_job_id)

  @classmethod
  def teardown_class(cls):
    try:
      Document.objects.filter(name__contains=cls.username).delete()
      Workflow.objects.filter(name__contains=cls.username).delete()
      # Remove user home directories.
      cls.cluster.fs.do_as_superuser(cls.cluster.fs.rmtree, cls.home_dir)
    except:
      LOG.exception('failed to teardown %s' % cls.home_dir)
    cls.cluster.fs.setuser(cls.prev_user)

  @classmethod
  def create_design(cls):
    job_name = '%s_%s' % (cls.username, 'sleep_job')
    if not Document.objects.available_docs(Workflow, cls.user).filter(name=job_name).exists():
      response = cls.client.post(reverse('jobsub.views.new_design',
        kwargs={'node_type': 'mapreduce'}),
        data={'name': job_name,
              'description': '',
              'node_type': 'mapreduce',
              'jar_path': '/user/hue/oozie/workspaces/lib/hadoop-examples.jar',
              'prepares': '[]',
              'files': '[]',
              'archives': '[]',
              'job_properties': '[{\"name\":\"mapred.reduce.tasks\",\"value\":\"1\"},{\"name\":\"mapred.mapper.class\",\"value\":\"org.apache.hadoop.examples.SleepJob\"},{\"name\":\"mapred.reducer.class\",\"value\":\"org.apache.hadoop.examples.SleepJob\"},{\"name\":\"mapred.mapoutput.key.class\",\"value\":\"org.apache.hadoop.io.IntWritable\"},{\"name\":\"mapred.mapoutput.value.class\",\"value\":\"org.apache.hadoop.io.NullWritable\"},{\"name\":\"mapred.output.format.class\",\"value\":\"org.apache.hadoop.mapred.lib.NullOutputFormat\"},{\"name\":\"mapred.input.format.class\",\"value\":\"org.apache.hadoop.examples.SleepJob$SleepInputFormat\"},{\"name\":\"mapred.partitioner.class\",\"value\":\"org.apache.hadoop.examples.SleepJob\"},{\"name\":\"mapred.speculative.execution\",\"value\":\"false\"},{\"name\":\"sleep.job.map.sleep.time\",\"value\":\"0\"},{\"name\":\"sleep.job.reduce.sleep.time\",\"value\":\"${REDUCER_SLEEP_TIME}\"}]'
        },
        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
      assert_equal(response.status_code, 200)

    return Document.objects.available_docs(Workflow, cls.user).get(name=job_name).content_object

  @classmethod
  def install_examples(cls):
    global _INITIALIZED
    if _INITIALIZED:
      return

    cls.client.post(reverse('oozie:install_examples'))
    cls.cluster.fs.do_as_user(cls.username, cls.cluster.fs.create_home_dir, cls.home_dir)
    cls.cluster.fs.do_as_superuser(cls.cluster.fs.chmod, cls.home_dir, 0777, True)

    _INITIALIZED = True

  def test_uncommon_views(self):
    """
    These views exist, but tend not to be ever called, because they're not in the normal UI.
    """
    raise SkipTest

    TestJobBrowserWithHadoop.client.get("/jobbrowser/clusterstatus")
    TestJobBrowserWithHadoop.client.get("/jobbrowser/queues")
    TestJobBrowserWithHadoop.client.get("/jobbrowser/jobbrowser")

  def test_failed_jobs(self):
    """
    Test jobs with genuine failure, not just killed
    """

    if is_live_cluster():
      raise SkipTest('HUE-2902: Skipping because test is not reentrant')

    # Create design that will fail because the script file isn't there
    INPUT_DIR = TestJobBrowserWithHadoop.home_dir + '/input'
    OUTPUT_DIR = TestJobBrowserWithHadoop.home_dir + '/output'
    try:
      TestJobBrowserWithHadoop.cluster.fs.mkdir(TestJobBrowserWithHadoop.home_dir + "/jt-test_failed_jobs")
      TestJobBrowserWithHadoop.cluster.fs.mkdir(INPUT_DIR)
      TestJobBrowserWithHadoop.cluster.fs.rmtree(OUTPUT_DIR)
    except:
      LOG.exception('failed to teardown tests')

    job_name = '%s_%s' % (TestJobBrowserWithHadoop.username, 'test_failed_jobs-1')
    response = TestJobBrowserWithHadoop.client.post(reverse('jobsub.views.new_design', kwargs={'node_type': 'mapreduce'}), {
        'name': [job_name],
        'description': ['description test_failed_jobs-1'],
        'args': '',
        'jar_path': '/user/hue/oozie/workspaces/lib/hadoop-examples.jar',
        'prepares': '[]',
        'archives': '[]',
        'files': '[]',
        'job_properties': ['[{"name":"mapred.input.dir","value":"%s"},\
            {"name":"mapred.output.dir","value":"%s"},\
            {"name":"mapred.mapper.class","value":"org.apache.hadoop.mapred.lib.dne"},\
            {"name":"mapred.combiner.class","value":"org.apache.hadoop.mapred.lib.dne"},\
            {"name":"mapred.reducer.class","value":"org.apache.hadoop.mapred.lib.dne"}]' % (INPUT_DIR, OUTPUT_DIR)]
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest', follow=True)

    # Submit the job
    design_dict = json.loads(response.content)
    design_id = int(design_dict['id'])
    response = TestJobBrowserWithHadoop.client.post(reverse('oozie:submit_workflow',
                                args=[design_id]),
                                data={u'form-MAX_NUM_FORMS': [u''],
                                      u'form-INITIAL_FORMS': [u'1'],
                                      u'form-0-name': [u'REDUCER_SLEEP_TIME'],
                                      u'form-0-value': [u'1'],
                                      u'form-TOTAL_FORMS': [u'1']},
                                follow=True)
    oozie_jobid = response.context[0]['oozie_workflow'].id
    job = OozieServerProvider.wait_until_completion(oozie_jobid)
    hadoop_job_id = get_hadoop_job_id(TestJobBrowserWithHadoop.oozie, oozie_jobid, 1)
    hadoop_job_id_short = views.get_shorter_id(hadoop_job_id)

    # Select only killed jobs (should be absent)
    # Taking advantage of the fact new jobs are at the top of the list!
    response = TestJobBrowserWithHadoop.client.post('/jobbrowser/jobs/', {'format': 'json', 'state': 'killed'})
    assert_false(hadoop_job_id_short in response.content)

    # Select only failed jobs (should be present)
    # Map job should succeed. Reduce job should fail.
    response = TestJobBrowserWithHadoop.client.post('/jobbrowser/jobs/', {'format': 'json', 'state': 'failed'})
    assert_true(hadoop_job_id_short in response.content)

    raise SkipTest # Not compatible with MR2

    # The single job view should have the failed task table
    response = TestJobBrowserWithHadoop.client.get('/jobbrowser/jobs/%s' % (hadoop_job_id,))
    html = response.content.lower()
    assert_true('failed task' in html, html)

    # The map task should say success (empty input)
    map_task_id = TestJobBrowserWithHadoop.hadoop_job_id.replace('job', 'task') + '_m_000000'
    response = TestJobBrowserWithHadoop.client.get('/jobbrowser/jobs/%s/tasks/%s' % (hadoop_job_id, map_task_id))
    assert_true('succeed' in response.content)
    assert_true('failed' not in response.content)

    # The reduce task should say failed
    reduce_task_id = hadoop_job_id.replace('job', 'task') + '_r_000000'
    response = TestJobBrowserWithHadoop.client.get('/jobbrowser/jobs/%s/tasks/%s' % (hadoop_job_id, reduce_task_id))
    assert_true('succeed' not in response.content)
    assert_true('failed' in response.content)

    # Selecting by failed state should include the failed map
    response = TestJobBrowserWithHadoop.client.get('/jobbrowser/jobs/%s/tasks?taskstate=failed' % (hadoop_job_id,))
    assert_true('r_000000' in response.content)
    assert_true('m_000000' not in response.content)

  def test_jobs_page(self):
    # All jobs page and fetch job ID
    # Taking advantage of the fact new jobs are at the top of the list!
    response = TestJobBrowserWithHadoop.client.post('/jobbrowser/jobs/', {'format': 'json'})
    assert_true(TestJobBrowserWithHadoop.hadoop_job_id_short in response.content, response.content)

    # Make sure job succeeded
    response = TestJobBrowserWithHadoop.client.post('/jobbrowser/jobs/', {'format': 'json', 'state': 'completed'})
    assert_true(TestJobBrowserWithHadoop.hadoop_job_id_short in response.content)
    response = TestJobBrowserWithHadoop.client.post('/jobbrowser/jobs/', {'format': 'json', 'state': 'failed'})
    assert_false(TestJobBrowserWithHadoop.hadoop_job_id_short in response.content)
    response = TestJobBrowserWithHadoop.client.post('/jobbrowser/jobs/', {'format': 'json', 'state': 'running'})
    assert_false(TestJobBrowserWithHadoop.hadoop_job_id_short in response.content)
    response = TestJobBrowserWithHadoop.client.post('/jobbrowser/jobs/', {'format': 'json', 'state': 'killed'})
    assert_false(TestJobBrowserWithHadoop.hadoop_job_id_short in response.content)

  def test_tasks_page(self):
    raise SkipTest

    # Test tracker page
    early_task_id = TestJobBrowserWithHadoop.hadoop_job_id.replace('job', 'task') + '_m_000000'
    response = TestJobBrowserWithHadoop.client.get('/jobbrowser/jobs/%s/tasks/%s' % (TestJobBrowserWithHadoop.hadoop_job_id, early_task_id))

    tracker_url = re.search('<a href="(/jobbrowser/trackers/.+?)"', response.content).group(1)
    response = TestJobBrowserWithHadoop.client.get(tracker_url)
    assert_true('Tracker at' in response.content)

  def test_job_permissions(self):
    # Login as ourself
    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = TestJobBrowserWithHadoop.client.post('/jobbrowser/jobs/', {'format': 'json', 'user': ''})
      assert_true(TestJobBrowserWithHadoop.hadoop_job_id_short in response.content)
    finally:
      finish()

    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = TestJobBrowserWithHadoop.client.post('/jobbrowser/jobs/', {'format': 'json', 'user': ''})
      assert_true(TestJobBrowserWithHadoop.hadoop_job_id_short in response.content)
    finally:
      finish()

    # Login as someone else
    client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test')
    grant_access("not_me", "test", "jobbrowser")

    finish = SHARE_JOBS.set_for_testing(True)
    try:
      response = client_not_me.post('/jobbrowser/jobs/', {'format': 'json', 'user': ''})
      assert_true(TestJobBrowserWithHadoop.hadoop_job_id_short in response.content)
    finally:
      finish()

    finish = SHARE_JOBS.set_for_testing(False)
    try:
      response = client_not_me.post('/jobbrowser/jobs/', {'format': 'json', 'user': ''})
      assert_false(TestJobBrowserWithHadoop.hadoop_job_id_short in response.content)
    finally:
      finish()

  def test_job_counter(self):
    raise SkipTest

    # Single job page
    response = TestJobBrowserWithHadoop.client.get('/jobbrowser/jobs/%s' % TestJobBrowserWithHadoop.hadoop_job_id)
    # Check some counters for single job.
    counters = response.context[0]['job'].counters
    counters_file_bytes_written = counters['org.apache.hadoop.mapreduce.FileSystemCounter']['counters']['FILE_BYTES_WRITTEN']
    assert_true(counters_file_bytes_written['map'] > 0)
    assert_true(counters_file_bytes_written['reduce'] > 0)

  def test_task_page(self):
    raise SkipTest

    response = TestJobBrowserWithHadoop.client.get('/jobbrowser/jobs/%s/tasks' % (TestJobBrowserWithHadoop.hadoop_job_id,))
    assert_true(len(response.context[0]['page'].object_list), 4)
    # Select by tasktype
    response = TestJobBrowserWithHadoop.client.get('/jobbrowser/jobs/%s/tasks?tasktype=reduce' % (TestJobBrowserWithHadoop.hadoop_job_id,))
    assert_true(len(response.context[0]['page'].object_list), 1)
    # Select by taskstate
    response = TestJobBrowserWithHadoop.client.get('/jobbrowser/jobs/%s/tasks?taskstate=succeeded' % (TestJobBrowserWithHadoop.hadoop_job_id,))
    assert_true(len(response.context[0]['page'].object_list), 4)
    # Select by text
    response = TestJobBrowserWithHadoop.client.get('/jobbrowser/jobs/%s/tasks?tasktext=clean' % (TestJobBrowserWithHadoop.hadoop_job_id,))
    assert_true(len(response.context[0]['page'].object_list), 1)

  def test_job_single_logs(self):
    if not is_live_cluster():
      raise SkipTest

    response = TestJobBrowserWithHadoop.client.get('/jobbrowser/jobs/%s/single_logs?format=json' % (TestJobBrowserWithHadoop.hadoop_job_id))
    json_resp = json.loads(response.content)

    assert_true('logs' in json_resp)
    assert_true('Log Type: stdout' in json_resp['logs'][1])
    assert_true('Log Type: stderr' in json_resp['logs'][2])
    assert_true('Log Type: syslog' in json_resp['logs'][3])

    # Verify that syslog contains log information for a completed oozie job
    match = re.search(r"^Log Type: syslog(.+)Log Length: (?P<log_length>\d+)(.+)$", json_resp['logs'][3], re.DOTALL)
    assert_true(match and match.group(2), 'Failed to parse log length from syslog')
    log_length = match.group(2)
    assert_true(log_length > 0, 'Log Length is 0, expected content in syslog.')


class TestMapReduce2NoHadoop:

  def setUp(self):
    # Beware: Monkey patching
    if not hasattr(resource_manager_api, 'old_get_resource_manager_api'):
      resource_manager_api.old_get_resource_manager = resource_manager_api.get_resource_manager
    if not hasattr(mapreduce_api, 'old_get_mapreduce_api'):
      mapreduce_api.old_get_mapreduce_api = mapreduce_api.get_mapreduce_api
    if not hasattr(history_server_api, 'old_get_history_server_api'):
      history_server_api.old_get_history_server_api = history_server_api.get_history_server_api
    if not hasattr(spark_history_server_api, 'old_get_spark_history_server_api'):
      spark_history_server_api.old_get_spark_history_server_api = spark_history_server_api.get_history_server_api


    self.c = make_logged_in_client(is_superuser=False)
    grant_access("test", "test", "jobbrowser")
    self.user = User.objects.get(username='test')

    self.c2 = make_logged_in_client(is_superuser=False, username="test2")
    grant_access("test2", "test2", "jobbrowser")
    self.user2 = User.objects.get(username='test2')

    self.c3 = make_logged_in_client(is_superuser=False, username="test3")
    grant_access("test3", "test3", "jobbrowser")
    self.user3 = User.objects.get(username='test3')

    resource_manager_api.get_resource_manager = lambda username: MockResourceManagerApi(username)
    mapreduce_api.get_mapreduce_api = lambda username: MockMapreduceApi(username)
    history_server_api.get_history_server_api = lambda username: HistoryServerApi(username)
    spark_history_server_api.get_history_server_api = lambda: MockSparkHistoryApi()

    self.finish = [
        YARN_CLUSTERS['default'].SUBMIT_TO.set_for_testing(True),
        SHARE_JOBS.set_for_testing(False)
    ]
    assert_true(cluster.is_yarn())


  def tearDown(self):
    resource_manager_api.get_resource_manager = getattr(resource_manager_api, 'old_get_resource_manager')
    mapreduce_api.get_mapreduce_api = getattr(mapreduce_api, 'old_get_mapreduce_api')
    history_server_api.get_history_server_api = getattr(history_server_api, 'old_get_history_server_api')
    spark_history_server_api.get_history_server_api = getattr(spark_history_server_api, 'old_get_spark_history_server_api')

    for f in self.finish:
      f()

  def test_jobs(self):
    response = self.c.post('/jobbrowser/', {'format': 'json'})
    response_content = json.loads(response.content)
    assert_equal(len(response_content['jobs']), 4)

    response = self.c.post('/jobbrowser/jobs/', {'format': 'json', 'text': 'W=MapReduce-copy2'})
    response_content = json.loads(response.content)
    assert_equal(len(response_content['jobs']), 1)

  def test_applications_no_start_time(self):
    response = self.c.post('/jobbrowser/', {'format': 'json'})
    data = json.loads(response.content)
    job = [j for j in data['jobs'] if j['id'] == 'application_1428442704693_0007']
    assert_true(job, job)
    job = job[0]

    assert_equal('', job['startTimeFormatted'], data)
    assert_equal('', job['durationFormatted'], data)

  def test_running_job(self):
    response = self.c.get('/jobbrowser/jobs/application_1356251510842_0054')
    assert_true('job_1356251510842_0054' in response.content, response.content)
    assert_true('RUNNING' in response.content)

    response = self.c.get('/jobbrowser/jobs/job_1356251510842_0054')
    assert_true('job_1356251510842_0054' in response.content)
    assert_true('RUNNING' in response.content)

  def test_application_no_start_time(self):
    response = self.c.get('/jobbrowser/jobs/application_1428442704693_0007?format=json')
    data = json.loads(response.content)

    assert_equal('', data['job']['startTimeFormatted'], data)
    assert_equal('', data['job']['durationFormatted'], data)

  def test_finished_job(self):
    response = self.c.get('/jobbrowser/jobs/application_1356251510842_0009')
    assert_equal(response.context[0]['job'].jobId, 'job_1356251510842_0009')

    response = self.c.get('/jobbrowser/jobs/job_1356251510842_0009')
    assert_equal(response.context[0]['job'].jobId, 'job_1356251510842_0009')

  def test_spark_job(self):
    response = self.c.get('/jobbrowser/jobs/application_1428442704693_0006')
    assert_equal(response.context[0]['job'].jobId, 'application_1428442704693_0006')

  def test_yarn_job(self):
    response = self.c.get('/jobbrowser/jobs/application_1428442704693_0007')
    assert_equal(response.context[0]['job'].jobId, 'job_1356251510842_0009')

  def job_not_assigned(self):
    response = self.c.get('/jobbrowser/jobs/job_1356251510842_0009/job_not_assigned//my_url')
    assert_equal(response.context[0]['jobid'], 'job_1356251510842_0009')
    assert_equal(response.context[0]['path'], '/my_url')

    response = self.c.get('/jobbrowser/jobs/job_1356251510842_0009/job_not_assigned//my_url?format=json')
    result = json.loads(response.content)
    assert_equal(result['status'], 0)

  def test_acls_job(self):
    response = self.c.get('/jobbrowser/jobs/job_1356251510842_0054') # Check in perm decorator
    assert_true(can_view_job('test', response.context[0]['job']))
    assert_true(can_modify_job('test', response.context[0]['job']))

    assert_true(can_view_job('test2', response.context[0]['job']))
    assert_false(can_modify_job('test2', response.context[0]['job']))

    assert_false(can_view_job('test3', response.context[0]['job']))
    assert_false(can_modify_job('test3', response.context[0]['job']))

    response2 = self.c3.get('/jobbrowser/jobs/job_1356251510842_0054')
    assert_true('don&#39;t have permission to access job' in response2.content, response2.content)

  def test_kill_job(self):
    job_id = 'application_1356251510842_0054'
    try:
      response = self.c.post('/jobbrowser/jobs/%s/kill?format=json' % job_id)
      assert_equal(json.loads(response.content), {"status": 0})
    finally:
      MockResourceManagerApi.APPS[job_id]['state'] = 'RUNNING'

    response = self.c2.post('/jobbrowser/jobs/%s/kill?format=json' % job_id)
    assert_true('Kill operation is forbidden.' in response.content, response.content)



class TestResourceManagerHaNoHadoop:

  def setUp(self):
    # Beware: Monkey patching
    if not hasattr(resource_manager_api, 'old_get_resource_manager_api'):
      resource_manager_api.old_ResourceManagerApi = resource_manager_api.ResourceManagerApi
    if not hasattr(mapreduce_api, 'old_get_mapreduce_api'):
      mapreduce_api.old_get_mapreduce_api = mapreduce_api.get_mapreduce_api
    if not hasattr(history_server_api, 'old_get_history_server_api'):
      history_server_api.old_get_history_server_api = history_server_api.get_history_server_api

    self.c = make_logged_in_client(is_superuser=False)
    grant_access("test", "test", "jobbrowser")
    self.user = User.objects.get(username='test')

    resource_manager_api.ResourceManagerApi =  MockResourceManagerHaApi
    mapreduce_api.get_mapreduce_api = lambda username: MockMapreduceHaApi(username)
    history_server_api.get_history_server_api = lambda username: HistoryServerHaApi(username)

    self.finish = []

  def tearDown(self):
    resource_manager_api.ResourceManagerApi = getattr(resource_manager_api, 'old_ResourceManagerApi')
    resource_manager_api.API_CACHE = None
    mapreduce_api.get_mapreduce_api = getattr(mapreduce_api, 'old_get_mapreduce_api')
    history_server_api.get_history_server_api = getattr(history_server_api, 'old_get_history_server_api')

    for f in self.finish:
      f()


  def test_failover_no_ha(self):
    self.finish = [
        YARN_CLUSTERS.set_for_testing({'default': {}}),

        YARN_CLUSTERS['default'].SUBMIT_TO.set_for_testing(True),
        YARN_CLUSTERS['default'].RESOURCE_MANAGER_API_URL.set_for_testing('rm_host_active'),
        YARN_CLUSTERS['default'].HISTORY_SERVER_API_URL.set_for_testing('jhs_host'),
        YARN_CLUSTERS['default'].SECURITY_ENABLED.set_for_testing(False),
        YARN_CLUSTERS['default'].SSL_CERT_CA_VERIFY.set_for_testing(False),
    ]

    resource_manager_api.API_CACHE = None
    api = get_api(self.user, jt=None)

    api.get_jobs(self.user, username=self.user.username, state='running', text='')
    assert_false(api.resource_manager_api.from_failover)

    api.get_jobs(self.user, username=self.user.username, state='running', text='')
    assert_false(api.resource_manager_api.from_failover)

    assert_raises(Exception, api.get_jobs, self.user, username=self.user.username, state='running', text='')


  def test_failover_ha(self):
    self.finish = [
        YARN_CLUSTERS.set_for_testing({'ha1': {}, 'ha2': {}}),

        YARN_CLUSTERS['ha1'].SUBMIT_TO.set_for_testing(True),
        YARN_CLUSTERS['ha1'].RESOURCE_MANAGER_API_URL.set_for_testing('rm_host_active'),
        YARN_CLUSTERS['ha1'].HISTORY_SERVER_API_URL.set_for_testing('jhs_host'),
        YARN_CLUSTERS['ha1'].SECURITY_ENABLED.set_for_testing(False),
        YARN_CLUSTERS['ha1'].SSL_CERT_CA_VERIFY.set_for_testing(False),
        YARN_CLUSTERS['ha2'].SUBMIT_TO.set_for_testing(True),
        YARN_CLUSTERS['ha2'].RESOURCE_MANAGER_API_URL.set_for_testing('rm_2_host'),
        YARN_CLUSTERS['ha2'].HISTORY_SERVER_API_URL.set_for_testing('jhs_host'),
        YARN_CLUSTERS['ha2'].SECURITY_ENABLED.set_for_testing(False),
        YARN_CLUSTERS['ha2'].SSL_CERT_CA_VERIFY.set_for_testing(False),
    ]


    resource_manager_api.API_CACHE = None
    api = get_api(self.user, jt=None)

    api.get_jobs(self.user, username=self.user.username, state='running', text='')
    assert_false(api.resource_manager_api.from_failover)

    api.get_jobs(self.user, username=self.user.username, state='running', text='')
    assert_false(api.resource_manager_api.from_failover)

    # rm1 is set to to fail the 3rd time
    YARN_CLUSTERS['ha1'].RESOURCE_MANAGER_API_URL.set_for_testing('rm_1_host')
    YARN_CLUSTERS['ha2'].RESOURCE_MANAGER_API_URL.set_for_testing('rm_2_host_active') # Just tells mocked RM that it should say it is active
    api.get_jobs(self.user, username=self.user.username, state='running', text='')
    assert_true(api.resource_manager_api.from_failover)
    api.resource_manager_api.from_failover = False

    api.get_jobs(self.user, username=self.user.username, state='running', text='')
    assert_false(api.resource_manager_api.from_failover)

    # rm2 is set to to fail the 3rd time
    YARN_CLUSTERS['ha1'].RESOURCE_MANAGER_API_URL.set_for_testing('rm_1_host_active')
    YARN_CLUSTERS['ha2'].RESOURCE_MANAGER_API_URL.set_for_testing('rm_2_host')
    api.get_jobs(self.user, username=self.user.username, state='running', text='')
    assert_true(api.resource_manager_api.from_failover)
    api.resource_manager_api.from_failover = False

    api.get_jobs(self.user, username=self.user.username, state='running', text='')
    assert_false(api.resource_manager_api.from_failover)

    # if rm fails and no other active ones we fail
    assert_raises(Exception, api.get_jobs, self.user, username=self.user.username, state='running', text='')


class TestImpalaApi(object):

  def setUp(self):
    api = MockImpalaQueryApi('http://url.com')
    self.api = QueryApi(None, impala_api=api)

  def test_apps(self):
    response = self.api.apps({})
    target = [{'status': u'FINISHED', 'rows_fetched': 28, 'user': u'admin', 'canWrite': False, 'duration': 3355000.0, 'id': u'8a46a8865624698f:b80b211500000000', 'apiStatus': 'SUCCEEDED', 'name': u'SELECT sample_07.description, sample_07.salary FROM   sample...', 'submitted': u'2017-10-25 15:38:26.637010000', 'queue': u'root.admin', 'waiting': True, 'progress': u'1 / 1 ( 100%)', 'type': u'QUERY', 'waiting_time': u'52m8s'}, {'status': u'FINISHED', 'rows_fetched': 53, 'user': u'admin', 'canWrite': False, 'duration': 3369000.0, 'id': u'4d497267f34ff17d:817bdfb500000000', 'apiStatus': 'SUCCEEDED', 'name': u'select * from customers', 'submitted': u'2017-10-25 15:38:12.872825000', 'queue': u'root.admin', 'waiting': True, 'progress': u'2 / 3 (66.6667%)', 'type': u'QUERY', 'waiting_time': u'52m8s'}]
    for i in range(0,len(target)):
      for key, value in target[i].iteritems():
        assert_equal(response.get('apps')[i].get(key), value)

  def test_app(self):
    response = self.api.app('4d497267f34ff17d:817bdfb500000000')
    for key, value in {'status': u'FINISHED', 'name': u'select * from customers',
      'duration': 3369000.0, 'progress': 66.6667, 'user': u'admin', 'type': 'queries',
      'id': '4d497267f34ff17d:817bdfb500000000', 'submitted': u'2017-10-25 15:38:12.872825000', 'apiStatus': 'SUCCEEDED', 'doc_url': 'http://url.com/query_plan?query_id=4d497267f34ff17d:817bdfb500000000'}.iteritems():
      assert_equal(response.get(key), value)

    response = self.api.app('8a46a8865624698f:b80b211500000000')

    for key, value in {'status': u'FINISHED',
      'name': u'SELECT sample_07.description, sample_07.salary FROM   sample...', 'duration': 3355000.0, 'progress': 100.0, 'user': u'admin',
      'type': 'queries', 'id': '8a46a8865624698f:b80b211500000000', 'submitted': u'2017-10-25 15:38:26.637010000',
      'apiStatus': 'SUCCEEDED', 'doc_url': 'http://url.com/query_plan?query_id=8a46a8865624698f:b80b211500000000'}.iteritems():
      assert_equal(response.get(key), value)


class TestSparkNoHadoop(object):
  def setUp(self):
    self.c = make_logged_in_client(is_superuser=False)
    grant_access("test", "test", "jobbrowser")
    self.user = User.objects.get(username='test')

    if not hasattr(job_api, 'old_NativeYarnApi'):
      job_api.old_NativeYarnApi = job_api.YarnApi

    if not hasattr(views, 'old_get_api'):
      views.old_get_api = views.get_api

    job_api.NativeYarnApi = MockYarnApi
    views.get_api = MockYarnApi

  def tearDown(self):
    job_api.NativeYarnApi = getattr(job_api, 'old_NativeYarnApi')
    views.get_api = getattr(views, 'old_get_api')

  def test_spark_executor_logs(self):
    # Spark job status is succeed
    query_executor_data = {u'interface': [u'"jobs"'], u'app_id': [u'"driver_executor_application_1513618343677_0018"']}
    resp_executor = self.c.post('/jobbrowser/api/job/jobs', query_executor_data)
    response_executor = json.loads(resp_executor.content)
    assert_equal(response_executor['status'], 0)
    assert_equal(response_executor['app']['executor_id'], 'driver')

    query_log_data = {u'interface': [u'"jobs"'], u'type': [u'"SPARK"'], u'app_id': [u'"application_1513618343677_0018"'], u'name': [u'"default"']}
    resp_log = self.c.post('/jobbrowser/api/job/logs', query_log_data)
    response_log = json.loads(resp_log.content)
    assert_equal(response_log['status'], 0)
    assert_equal(response_log['logs']['logs'], 'dummy_logs')

    # Spark job status is running
    query_executor_data = {u'interface': [u'"jobs"'], u'app_id': [u'"driver_executor_application_1513618343677_0020"']}
    resp_executor = self.c.post('/jobbrowser/api/job/jobs', query_executor_data)
    response_executor = json.loads(resp_executor.content)
    assert_equal(response_executor['status'], 0)
    assert_equal(response_executor['app']['executor_id'], 'driver')

    query_log_data = {u'interface': [u'"jobs"'], u'type': [u'"SPARK"'], u'app_id': [u'"application_1513618343677_0020"'], u'name': [u'"default"']}
    resp_log = self.c.post('/jobbrowser/api/job/logs', query_log_data)
    response_log = json.loads(resp_log.content)
    assert_equal(response_log['status'], 0)
    assert_equal(response_log['logs']['logs'], 'dummy_logs')


class MockYarnApi:
  def __init__(self, user, jt=None):
    self.user = user

  def get_job(self, jobid):
    return MockSparkJob(app_id=jobid)


class MockSparkJob(SparkJob):
  def __init__(self, app_id):
    self.history_server_api = MockSparkHistoryApi()
    self.jobId = app_id
    self.trackingUrl = 'http://localhost:8088/proxy/' + app_id

    if app_id == 'application_1513618343677_0018':
      self.status = 'SUCCEEDED'
    elif app_id == 'application_1513618343677_0020':
      self.status = 'RUNNING'

    self._get_metrics()


class MockResourceManagerHaApi(object):
  """
  Mock the RM API.
  Raise a failover exception after 2 calls. Is active if name contains 'active'.
  """
  def __init__(self, rm_url, security_enabled=False, ssl_cert_ca_verify=False):
    self.rm_url = rm_url
    self.from_failover = False
    self.get_apps_count = 0

  def setuser(self, user):
    return user

  @property
  def user(self):
    return 'test'

  @property
  def username(self):
    return 'test'

  @property
  def url(self):
    return self.rm_url

  def apps(self, **kwargs):
    if self.get_apps_count >= 2:
      self.get_apps_count = 0
      raise Exception('standby RM after 2 tries')

    self.get_apps_count += 1
    return {
      'apps': {
         'app': []
      }
    }

  def cluster(self):
    return {'clusterInfo': {'haState': 'ACTIVE' if 'active' in self.rm_url else 'STANDBY'}}


class MockMapreduceHaApi(object):
  def __init__(self, username): pass


class HistoryServerHaApi(object):
  def __init__(self, username): pass


class MockResourceManagerApi:
  APPS = {
    'application_1356251510842_0054': {
        u'finishedTime': 1356961070119,
        u'name': u'oozie:launcher:T=map-reduce:W=MapReduce-copy:A=Sleep:ID=0000004-121223003201296-oozie-oozi-W',
        u'amContainerLogs': u'http://localhost:8042/node/containerlogs/container_1356251510842_0054_01_000001/romain',
        u'clusterId': 1356251510842,
        u'trackingUrl': u'http://localhost:8088/proxy/application_1356251510842_0054/jobhistory/job/job_1356251510842_0054',
        u'amHostHttpAddress': u'localhost:8042',
        u'startedTime': 1356961057225,
        u'queue': u'default',
        u'state': u'RUNNING',
        u'elapsedTime': 12894,
        u'finalStatus': u'UNDEFINED',
        u'diagnostics': u'',
        u'progress': 100.0,
        u'trackingUI': u'History',
        u'id': u'application_1356251510842_0054',
        u'user': u'test',
        # For when the job is KILLED
        u'startTime': 1356961057226,
        u'finishTime': 1356961057226,
        u'applicationType': 'MAPREDUCE'
    },
    'application_1356251510842_0009': {
        u'finishedTime': 1356467118570,
        u'name': u'oozie:action:T=map-reduce:W=MapReduce-copy2:A=Sleep:ID=0000002-121223003201296-oozie-oozi-W',
        u'amContainerLogs': u'http://localhost:8042/node/containerlogs/container_1356251510842_0009_01_000001/romain',
        u'clusterId': 1356251510842,
        u'trackingUrl': u'http://localhost:8088/proxy/application_1356251510842_0009/jobhistory/job/job_1356251510842_0009',
        u'amHostHttpAddress': u'localhost:8042',
        u'startedTime': 1356467081121,
        u'queue': u'default',
        u'state': u'FINISHED',
        u'elapsedTime': 37449,
        u'finalStatus': u'SUCCEEDED',
        u'diagnostics': u'',
        u'progress': 100.0,
        u'trackingUI': u'History',
        u'id': u'application_1356251510842_0009',
        u'user': u'test',
        u'applicationType': 'MAPREDUCE'
    },
    'application_1428442704693_0006': {
        u'allocatedMB': 4096,
        u'allocatedVCores': 3,
        u'amContainerLogs': u'http://localhost:8042/node/containerlogs/container_1428442704693_0006_01_000001/erickt',
        u'amHostHttpAddress': u'localhost:8042',
        u'applicationTags': u'',
        u'applicationType': u'SPARK',
        u'clusterId': 1428442704693,
        u'diagnostics': u'',
        u'elapsedTime': 529040,
        u'finalStatus': u'UNDEFINED',
        u'finishedTime': 0,
        u'id': u'application_1428442704693_0006',
        u'memorySeconds': 2138468,
        u'name': u'Spark shell',
        u'numAMContainerPreempted': 0,
        u'numNonAMContainerPreempted': 0,
        u'preemptedResourceMB': 0,
        u'preemptedResourceVCores': 0,
        u'progress': 10.0,
        u'queue': u'root.erickt',
        u'runningContainers': 3,
        u'startedTime': 1428443335161,
        u'state': u'RUNNING',
        u'trackingUI': u'ApplicationMaster',
        u'trackingUrl': u'http://localhost:8088/proxy/application_1428442704693_0006/',
        u'user': u'test',
        u'vcoreSeconds': 1567,
    },
    'application_1428442704693_0007': {
        u'allocatedMB': -1,
        u'allocatedVCores': -1,
        u'applicationTags': u'',
        u'applicationType': u'YARN',
        u'clusterId': 1428442704693,
        u'diagnostics': u'',
        u'elapsedTime': 4056,
        u'finalStatus': u'SUCCEEDED',
        u'finishedTime': 1428454945371,
        u'id': u'application_1428442704693_0007',
        u'memorySeconds': 2290,
        u'name': u'UnmanagedAM',
        u'numAMContainerPreempted': 0,
        u'numNonAMContainerPreempted': 0,
        u'preemptedResourceMB': 0,
        u'preemptedResourceVCores': 0,
        u'progress': 100.0,
        u'queue': u'root.erickt',
        u'runningContainers': -1,
        u'startedTime': 0,
        u'state': u'FINISHED',
        u'trackingUI': u'History',
        u'trackingUrl': u'http://N/A',
        u'user': u'test',
        u'vcoreSeconds': 1,
    }
  }

  def __init__(self, user, rm_url=None): pass

  def apps(self, **kwargs):
    return {
     'apps': {
       'app': [
         # RUNNING
         MockResourceManagerApi.APPS['application_1356251510842_0054'],
         # FINISHED
         MockResourceManagerApi.APPS['application_1356251510842_0009'],
         # SPARK
         MockResourceManagerApi.APPS['application_1428442704693_0006'],
         # YARN
         MockResourceManagerApi.APPS['application_1428442704693_0007'],
        ]
      }
    }

  def app(self, job_id):
    return {
      u'app': MockResourceManagerApi.APPS[job_id]
    }

class MockImpalaQueryApi:
  APPS = {
    '8a46a8865624698f:b80b211500000000': {u'stmt_type': u'QUERY', u'resource_pool': u'root.admin', u'waiting': True, u'last_event': u'Unregister query', u'start_time': u'2017-10-25 15:38:26.637010000', u'rows_fetched': 28, u'stmt': u'SELECT sample_07.description, sample_07.salary\r\nFROM\r\n  sample_07\r\nWHERE\r\n( sample_07.salary > 100000)\r\nORDER BY sample_07.salary DESC\r\nLIMIT 1000', u'executing': False, u'state': u'FINISHED', u'query_id': u'8a46a8865624698f:b80b211500000000', u'end_time': u'2017-10-25 16:34:22.592036000', u'duration': u'55m55s', u'progress': u'1 / 1 ( 100%)', u'effective_user': u'admin', u'default_db': u'default', u'waiting_time': u'52m8s'},
    '4d497267f34ff17d:817bdfb500000000': {u'stmt_type': u'QUERY', u'resource_pool': u'root.admin', u'waiting': True, u'last_event': u'Unregister query', u'start_time': u'2017-10-25 15:38:12.872825000', u'rows_fetched': 53, u'stmt': u'select * from customers', u'executing': False, u'state': u'FINISHED', u'query_id': u'4d497267f34ff17d:817bdfb500000000', u'end_time': u'2017-10-25 16:34:22.589811000', u'duration': u'56m9s', u'progress': u'2 / 3 (66.6667%)', u'effective_user': u'admin', u'default_db': u'default', u'waiting_time': u'52m8s'}
  }
  PLAN = {
    '4d497267f34ff17d:817bdfb500000000': {'status': -1, u'plan': {u'status': u'OK', u'plan_json': {u'plan_nodes': [{u'num_instances': 1, u'output_card': 53, u'label_detail': u'UNPARTITIONED', u'label': u'01:EXCHANGE', u'is_broadcast': True, u'max_time': u'0.000ns', u'avg_time': u'0.000ns', u'children': [], u'max_time_val': 0}, {u'num_instances': 1, u'output_card': 53, u'label_detail': u'default.customers', u'data_stream_target': u'01:EXCHANGE', u'label': u'00:SCAN HDFS', u'max_time': u'215.018ms', u'avg_time': u'215.018ms', u'children': [], u'max_time_val': 215018404}]}, u'__common__': {u'navbar': [{u'link': u'/backends', u'title': u'/backends'}, {u'link': u'/catalog', u'title': u'/catalog'}, {u'link': u'/hadoop-varz', u'title': u'/hadoop-varz'}, {u'link': u'/log_level', u'title': u'/log_level'}, {u'link': u'/logs', u'title': u'/logs'}, {u'link': u'/memz', u'title': u'/memz'}, {u'link': u'/metrics', u'title': u'/metrics'}, {u'link': u'/queries', u'title': u'/queries'}, {u'link': u'/rpcz', u'title': u'/rpcz'}, {u'link': u'/sessions', u'title': u'/sessions'}, {u'link': u'/threadz', u'title': u'/threadz'}, {u'link': u'/varz', u'title': u'/varz'}], u'process-name': u'impalad'}, u'stmt': u'select * from customers', u'summary': u'\nOperator       #Hosts   Avg Time   Max Time  #Rows  Est. #Rows  Peak Mem  Est. Peak Mem  Detail            \n-----------------------------------------------------------------------------------------------------------\n01:EXCHANGE         1    0.000ns    0.000ns     53           0         0              0  UNPARTITIONED     \n00:SCAN HDFS        1  215.018ms  215.018ms     53           0  45.02 KB       32.00 MB  default.customers ', u'query_id': u'1a48b5796f8f07f5:49ba9e6b00000000', u'plan': u'\n----------------\nPer-Host Resource Reservation: Memory=0B\nPer-Host Resource Estimates: Memory=32.00MB\nWARNING: The following tables have potentially corrupt table statistics.\nDrop and re-compute statistics to resolve this problem.\ndefault.customers\nWARNING: The following tables are missing relevant table and/or column statistics.\ndefault.customers\n\nF01:PLAN FRAGMENT [UNPARTITIONED] hosts=1 instances=1\nPLAN-ROOT SINK\n|  mem-estimate=0B mem-reservation=0B\n|\n01:EXCHANGE [UNPARTITIONED]\n|  mem-estimate=0B mem-reservation=0B\n|  tuple-ids=0 row-size=19B cardinality=0\n|\nF00:PLAN FRAGMENT [RANDOM] hosts=1 instances=1\n00:SCAN HDFS [default.customers, RANDOM]\n   partitions=1/1 files=1 size=15.44KB\n   table stats: 0 rows total\n   column stats: unavailable\n   mem-estimate=32.00MB mem-reservation=0B\n   tuple-ids=0 row-size=19B cardinality=0\n----------------'}},
    '8a46a8865624698f:b80b211500000000': {'status': -1, u'plan': {u'status': u'OK', u'plan_json': {u'plan_nodes': [{u'num_instances': 1, u'output_card': 28, u'label_detail': u'UNPARTITIONED', u'label': u'02:MERGING-EXCHANGE', u'is_broadcast': True, u'max_time': u'0.000ns', u'avg_time': u'0.000ns', u'children': [], u'max_time_val': 0}, {u'num_instances': 1, u'output_card': 28, u'label_detail': u'', u'data_stream_target': u'02:MERGING-EXCHANGE', u'label': u'01:TOP-N', u'max_time': u'0.000ns', u'avg_time': u'0.000ns', u'children': [{u'num_instances': 1, u'output_card': 28, u'label_detail': u'default.sample_07', u'label': u'00:SCAN HDFS', u'max_time': u'250.020ms', u'avg_time': u'250.020ms', u'children': [], u'max_time_val': 250020583}], u'max_time_val': 0}]}, u'__common__': {u'navbar': [{u'link': u'/backends', u'title': u'/backends'}, {u'link': u'/catalog', u'title': u'/catalog'}, {u'link': u'/hadoop-varz', u'title': u'/hadoop-varz'}, {u'link': u'/log_level', u'title': u'/log_level'}, {u'link': u'/logs', u'title': u'/logs'}, {u'link': u'/memz', u'title': u'/memz'}, {u'link': u'/metrics', u'title': u'/metrics'}, {u'link': u'/queries', u'title': u'/queries'}, {u'link': u'/rpcz', u'title': u'/rpcz'}, {u'link': u'/sessions', u'title': u'/sessions'}, {u'link': u'/threadz', u'title': u'/threadz'}, {u'link': u'/varz', u'title': u'/varz'}], u'process-name': u'impalad'}, u'stmt': u'SELECT sample_07.description, sample_07.salary\r\nFROM\r\n  sample_07\r\nWHERE\r\n( sample_07.salary > 100000)\r\nORDER BY sample_07.salary DESC\r\nLIMIT 1000', u'summary': u'\nOperator              #Hosts   Avg Time   Max Time  #Rows  Est. #Rows   Peak Mem  Est. Peak Mem  Detail            \n-------------------------------------------------------------------------------------------------------------------\n02:MERGING-EXCHANGE        1    0.000ns    0.000ns     28           0          0              0  UNPARTITIONED     \n01:TOP-N                   1    0.000ns    0.000ns     28           0   80.00 KB              0                    \n00:SCAN HDFS               1  250.020ms  250.020ms     28           0  173.00 KB       32.00 MB  default.sample_07 ', u'query_id': u'd424420e0c44ab9:c637ac2900000000', u'plan': u'\n----------------\nPer-Host Resource Reservation: Memory=0B\nPer-Host Resource Estimates: Memory=32.00MB\nWARNING: The following tables have potentially corrupt table statistics.\nDrop and re-compute statistics to resolve this problem.\ndefault.sample_07\nWARNING: The following tables are missing relevant table and/or column statistics.\ndefault.sample_07\n\nF01:PLAN FRAGMENT [UNPARTITIONED] hosts=1 instances=1\nPLAN-ROOT SINK\n|  mem-estimate=0B mem-reservation=0B\n|\n02:MERGING-EXCHANGE [UNPARTITIONED]\n|  order by: salary DESC\n|  limit: 1000\n|  mem-estimate=0B mem-reservation=0B\n|  tuple-ids=1 row-size=19B cardinality=0\n|\nF00:PLAN FRAGMENT [RANDOM] hosts=1 instances=1\n01:TOP-N [LIMIT=1000]\n|  order by: salary DESC\n|  mem-estimate=0B mem-reservation=0B\n|  tuple-ids=1 row-size=19B cardinality=0\n|\n00:SCAN HDFS [default.sample_07, RANDOM]\n   partitions=1/1 files=1 size=44.98KB\n   predicates: (sample_07.salary > 100000)\n   table stats: 0 rows total\n   column stats: unavailable\n   parquet dictionary predicates: (sample_07.salary > 100000)\n   mem-estimate=32.00MB mem-reservation=0B\n   tuple-ids=0 row-size=19B cardinality=0\n----------------'}}
  }
  PROFILE = {
    '4d497267f34ff17d:817bdfb500000000': {u'profile': u'Query (id=1a48b5796f8f07f5:49ba9e6b00000000):\n  Summary:\n    Session ID: 3348564c97187569:1c17ce45bdfbf0b2\n    Session Type: HIVESERVER2\n    HiveServer2 Protocol Version: V6\n    Start Time: 2017-10-26 11:19:40.420511000\n    End Time: 2017-10-26 11:23:11.426921000\n    Query Type: QUERY\n    Query State: FINISHED\n    Query Status: OK\n    Impala Version: impalad version 2.9.0-cdh5.12.1 RELEASE (build 6dacae08a283a36bb932335ae0c046977e2474e8)\n    User: admin\n    Connected User: admin\n    Delegated User: \n    Network Address: 10.16.2.226:63745\n    Default Db: default\n    Sql Statement: select * from customers\n    Coordinator: nightly512-unsecure-2.gce.cloudera.com:22000\n    Query Options (set by configuration): QUERY_TIMEOUT_S=600\n    Query Options (set by configuration and planner): QUERY_TIMEOUT_S=600,MT_DOP=0\n    Plan: \n----------------\nPer-Host Resource Reservation: Memory=0B\nPer-Host Resource Estimates: Memory=32.00MB\nWARNING: The following tables have potentially corrupt table statistics.\nDrop and re-compute statistics to resolve this problem.\ndefault.customers\nWARNING: The following tables are missing relevant table and/or column statistics.\ndefault.customers\n\nF01:PLAN FRAGMENT [UNPARTITIONED] hosts=1 instances=1\nPLAN-ROOT SINK\n|  mem-estimate=0B mem-reservation=0B\n|\n01:EXCHANGE [UNPARTITIONED]\n|  mem-estimate=0B mem-reservation=0B\n|  tuple-ids=0 row-size=19B cardinality=0\n|\nF00:PLAN FRAGMENT [RANDOM] hosts=1 instances=1\n00:SCAN HDFS [default.customers, RANDOM]\n   partitions=1/1 files=1 size=15.44KB\n   table stats: 0 rows total\n   column stats: unavailable\n   mem-estimate=32.00MB mem-reservation=0B\n   tuple-ids=0 row-size=19B cardinality=0\n----------------\n    Estimated Per-Host Mem: 33554432\n    Per-Host Memory Reservation: 0\n    Tables Missing Stats: default.customers\n    Tables With Corrupt Table Stats: default.customers\n    Request Pool: root.admin\n    Admission result: Admitted immediately\n    ExecSummary: \nOperator       #Hosts   Avg Time   Max Time  #Rows  Est. #Rows  Peak Mem  Est. Peak Mem  Detail            \n-----------------------------------------------------------------------------------------------------------\n01:EXCHANGE         1    0.000ns    0.000ns     53           0         0              0  UNPARTITIONED     \n00:SCAN HDFS        1  215.018ms  215.018ms     53           0  45.02 KB       32.00 MB  default.customers \n    Errors: \n    Planner Timeline: 5s043ms\n       - Metadata load started: 10.215ms (10.215ms)\n       - Metadata load finished: 4s789ms (4s779ms)\n       - Analysis finished: 4s856ms (66.876ms)\n       - Equivalence classes computed: 4s894ms (38.233ms)\n       - Single node plan created: 4s945ms (50.928ms)\n       - Runtime filters computed: 4s947ms (2.464ms)\n       - Distributed plan created: 4s953ms (5.784ms)\n       - Lineage info computed: 4s955ms (2.144ms)\n       - Planning finished: 5s043ms (88.082ms)\n    Query Timeline: 3m31s\n       - Query submitted: 0.000ns (0.000ns)\n       - Planning finished: 5s061ms (5s061ms)\n       - Submit for admission: 5s062ms (1.000ms)\n       - Completed admission: 5s062ms (0.000ns)\n       - Ready to start on 1 backends: 5s062ms (0.000ns)\n       - All 1 execution backends (2 fragment instances) started: 5s064ms (2.000ms)\n       - Rows available: 5s311ms (247.021ms)\n       - First row fetched: 6s565ms (1s254ms)\n       - Unregister query: 3m31s (3m24s)\n     - ComputeScanRangeAssignmentTimer: 0.000ns\n  ImpalaServer:\n     - ClientFetchWaitTimer: 3m25s\n     - RowMaterializationTimer: 1.000ms\n  Execution Profile 1a48b5796f8f07f5:49ba9e6b00000000:(Total: 250.021ms, non-child: 0.000ns, % non-child: 0.00%)\n    Number of filters: 0\n    Filter routing table: \n ID  Src. Node  Tgt. Node(s)  Target type  Partition filter  Pending (Expected)  First arrived  Completed   Enabled\n-------------------------------------------------------------------------------------------------------------------\n\n    Backend startup latencies: Count: 1, min / max: 1ms / 1ms, 25th %-ile: 1ms, 50th %-ile: 1ms, 75th %-ile: 1ms, 90th %-ile: 1ms, 95th %-ile: 1ms, 99.9th %-ile: 1ms\n    Per Node Peak Memory Usage: nightly512-unsecure-2.gce.cloudera.com:22000(71.09 KB) \n     - FiltersReceived: 0 (0)\n     - FinalizationTimer: 0.000ns\n    Averaged Fragment F01:(Total: 1s501ms, non-child: 1s256ms, % non-child: 83.68%)\n      split sizes:  min: 0, max: 0, avg: 0, stddev: 0\n      completion times: min:1s501ms  max:1s501ms  mean: 1s501ms  stddev:0.000ns\n      execution rates: min:0.00 /sec  max:0.00 /sec  mean:0.00 /sec  stddev:0.00 /sec\n      num instances: 1\n       - AverageThreadTokens: 0.00 \n       - BloomFilterBytes: 0\n       - PeakMemoryUsage: 12.41 KB (12712)\n       - PerHostPeakMemUsage: 71.09 KB (72800)\n       - RowsProduced: 53 (53)\n       - TotalNetworkReceiveTime: 219.018ms\n       - TotalNetworkSendTime: 0.000ns\n       - TotalStorageWaitTime: 0.000ns\n       - TotalThreadsInvoluntaryContextSwitches: 0 (0)\n       - TotalThreadsTotalWallClockTime: 1s473ms\n         - TotalThreadsSysTime: 9.000us\n         - TotalThreadsUserTime: 233.000us\n       - TotalThreadsVoluntaryContextSwitches: 3 (3)\n      Fragment Instance Lifecycle Timings:\n         - ExecTime: 1s254ms\n           - ExecTreeExecTime: 0.000ns\n         - OpenTime: 219.018ms\n           - ExecTreeOpenTime: 219.018ms\n         - PrepareTime: 28.002ms\n           - ExecTreePrepareTime: 0.000ns\n      BlockMgr:\n         - BlockWritesOutstanding: 0 (0)\n         - BlocksCreated: 0 (0)\n         - BlocksRecycled: 0 (0)\n         - BufferedPins: 0 (0)\n         - MaxBlockSize: 8.00 MB (8388608)\n         - MemoryLimit: 16.33 GB (17534060544)\n         - PeakMemoryUsage: 0\n         - ScratchBytesRead: 0\n         - ScratchBytesWritten: 0\n         - ScratchFileUsedBytes: 0\n         - ScratchReads: 0 (0)\n         - ScratchWrites: 0 (0)\n         - TotalBufferWaitTime: 0.000ns\n         - TotalEncryptionTime: 0.000ns\n         - TotalReadBlockTime: 0.000ns\n      PLAN_ROOT_SINK:\n         - PeakMemoryUsage: 0\n      CodeGen:(Total: 26.002ms, non-child: 26.002ms, % non-child: 100.00%)\n         - CodegenTime: 0.000ns\n         - CompileTime: 0.000ns\n         - LoadTime: 0.000ns\n         - ModuleBitcodeSize: 1.98 MB (2077616)\n         - NumFunctions: 0 (0)\n         - NumInstructions: 0 (0)\n         - OptimizationTime: 0.000ns\n         - PeakMemoryUsage: 0\n         - PrepareTime: 25.002ms\n      EXCHANGE_NODE (id=1):(Total: 219.018ms, non-child: 219.018ms, % non-child: 100.00%)\n         - BytesReceived: 1.54 KB (1578)\n         - ConvertRowBatchTime: 0.000ns\n         - DeserializeRowBatchTimer: 0.000ns\n         - FirstBatchArrivalWaitTime: 219.018ms\n         - PeakMemoryUsage: 0\n         - RowsReturned: 53 (53)\n         - RowsReturnedRate: 241.00 /sec\n         - SendersBlockedTimer: 0.000ns\n         - SendersBlockedTotalTimer(*): 0.000ns\n    Coordinator Fragment F01:\n      Instance 1a48b5796f8f07f5:49ba9e6b00000000 (host=nightly512-unsecure-2.gce.cloudera.com:22000):(Total: 1s501ms, non-child: 1s256ms, % non-child: 83.68%)\n        MemoryUsage(500.000ms): 12.00 KB, 12.00 KB, 12.00 KB\n         - AverageThreadTokens: 0.00 \n         - BloomFilterBytes: 0\n         - PeakMemoryUsage: 12.41 KB (12712)\n         - PerHostPeakMemUsage: 71.09 KB (72800)\n         - RowsProduced: 53 (53)\n         - TotalNetworkReceiveTime: 219.018ms\n         - TotalNetworkSendTime: 0.000ns\n         - TotalStorageWaitTime: 0.000ns\n         - TotalThreadsInvoluntaryContextSwitches: 0 (0)\n         - TotalThreadsTotalWallClockTime: 1s473ms\n           - TotalThreadsSysTime: 9.000us\n           - TotalThreadsUserTime: 233.000us\n         - TotalThreadsVoluntaryContextSwitches: 3 (3)\n        Fragment Instance Lifecycle Timings:\n           - ExecTime: 1s254ms\n             - ExecTreeExecTime: 0.000ns\n           - OpenTime: 219.018ms\n             - ExecTreeOpenTime: 219.018ms\n           - PrepareTime: 28.002ms\n             - ExecTreePrepareTime: 0.000ns\n        BlockMgr:\n           - BlockWritesOutstanding: 0 (0)\n           - BlocksCreated: 0 (0)\n           - BlocksRecycled: 0 (0)\n           - BufferedPins: 0 (0)\n           - MaxBlockSize: 8.00 MB (8388608)\n           - MemoryLimit: 16.33 GB (17534060544)\n           - PeakMemoryUsage: 0\n           - ScratchBytesRead: 0\n           - ScratchBytesWritten: 0\n           - ScratchFileUsedBytes: 0\n           - ScratchReads: 0 (0)\n           - ScratchWrites: 0 (0)\n           - TotalBufferWaitTime: 0.000ns\n           - TotalEncryptionTime: 0.000ns\n           - TotalReadBlockTime: 0.000ns\n        PLAN_ROOT_SINK:\n           - PeakMemoryUsage: 0\n        CodeGen:(Total: 26.002ms, non-child: 26.002ms, % non-child: 100.00%)\n           - CodegenTime: 0.000ns\n           - CompileTime: 0.000ns\n           - LoadTime: 0.000ns\n           - ModuleBitcodeSize: 1.98 MB (2077616)\n           - NumFunctions: 0 (0)\n           - NumInstructions: 0 (0)\n           - OptimizationTime: 0.000ns\n           - PeakMemoryUsage: 0\n           - PrepareTime: 25.002ms\n        EXCHANGE_NODE (id=1):(Total: 219.018ms, non-child: 0.000ns, % non-child: 0.00%)\n          BytesReceived(500.000ms): 1.54 KB, 1.54 KB, 1.54 KB\n           - BytesReceived: 1.54 KB (1578)\n           - ConvertRowBatchTime: 0.000ns\n           - DeserializeRowBatchTimer: 0.000ns\n           - FirstBatchArrivalWaitTime: 219.018ms\n           - PeakMemoryUsage: 0\n           - RowsReturned: 53 (53)\n           - RowsReturnedRate: 241.00 /sec\n           - SendersBlockedTimer: 0.000ns\n           - SendersBlockedTotalTimer(*): 0.000ns\n    Averaged Fragment F00:(Total: 241.020ms, non-child: 0.000ns, % non-child: 0.00%)\n      split sizes:  min: 15.44 KB, max: 15.44 KB, avg: 15.44 KB, stddev: 0\n      completion times: min:248.021ms  max:248.021ms  mean: 248.021ms  stddev:0.000ns\n      execution rates: min:62.26 KB/sec  max:62.26 KB/sec  mean:62.26 KB/sec  stddev:0.61 B/sec\n      num instances: 1\n       - AverageThreadTokens: 0.00 \n       - BloomFilterBytes: 0\n       - PeakMemoryUsage: 63.09 KB (64608)\n       - PerHostPeakMemUsage: 71.09 KB (72800)\n       - RowsProduced: 53 (53)\n       - TotalNetworkReceiveTime: 0.000ns\n       - TotalNetworkSendTime: 0.000ns\n       - TotalStorageWaitTime: 175.014ms\n       - TotalThreadsInvoluntaryContextSwitches: 2 (2)\n       - TotalThreadsTotalWallClockTime: 378.032ms\n         - TotalThreadsSysTime: 1.998ms\n         - TotalThreadsUserTime: 24.546ms\n       - TotalThreadsVoluntaryContextSwitches: 13 (13)\n      Fragment Instance Lifecycle Timings:\n         - ExecTime: 176.015ms\n           - ExecTreeExecTime: 176.015ms\n         - OpenTime: 26.002ms\n           - ExecTreeOpenTime: 1.000ms\n         - PrepareTime: 39.003ms\n           - ExecTreePrepareTime: 19.001ms\n      DataStreamSender (dst_id=1):\n         - BytesSent: 1.54 KB (1578)\n         - NetworkThroughput(*): 0.00 /sec\n         - OverallThroughput: 0.00 /sec\n         - PeakMemoryUsage: 6.09 KB (6240)\n         - RowsReturned: 53 (53)\n         - SerializeBatchTime: 0.000ns\n         - TransmitDataRPCTime: 0.000ns\n         - UncompressedRowBatchSize: 2.05 KB (2098)\n      CodeGen:(Total: 43.003ms, non-child: 43.003ms, % non-child: 100.00%)\n         - CodegenTime: 1.000ms\n         - CompileTime: 13.001ms\n         - LoadTime: 0.000ns\n         - ModuleBitcodeSize: 1.98 MB (2077616)\n         - NumFunctions: 5 (5)\n         - NumInstructions: 98 (98)\n         - OptimizationTime: 11.000ms\n         - PeakMemoryUsage: 49.00 KB (50176)\n         - PrepareTime: 18.001ms\n      HDFS_SCAN_NODE (id=0):(Total: 215.018ms, non-child: 215.018ms, % non-child: 100.00%)\n         - AverageHdfsReadThreadConcurrency: 0.00 \n         - AverageScannerThreadConcurrency: 0.00 \n         - BytesRead: 16.71 KB (17111)\n         - BytesReadDataNodeCache: 0\n         - BytesReadLocal: 16.71 KB (17111)\n         - BytesReadRemoteUnexpected: 0\n         - BytesReadShortCircuit: 16.71 KB (17111)\n         - DecompressionTime: 0.000ns\n         - MaxCompressedTextFileLength: 0\n         - NumColumns: 2 (2)\n         - NumDictFilteredRowGroups: 0 (0)\n         - NumDisksAccessed: 1 (1)\n         - NumRowGroups: 1 (1)\n         - NumScannerThreadsStarted: 1 (1)\n         - NumScannersWithNoReads: 0 (0)\n         - NumStatsFilteredRowGroups: 0 (0)\n         - PeakMemoryUsage: 45.02 KB (46101)\n         - PerReadThreadRawHdfsThroughput: 0.00 /sec\n         - RemoteScanRanges: 0 (0)\n         - RowBatchQueueGetWaitTime: 176.015ms\n         - RowBatchQueuePutWaitTime: 0.000ns\n         - RowsRead: 53 (53)\n         - RowsReturned: 53 (53)\n         - RowsReturnedRate: 246.00 /sec\n         - ScanRangesComplete: 1 (1)\n         - ScannerThreadsInvoluntaryContextSwitches: 0 (0)\n         - ScannerThreadsTotalWallClockTime: 176.015ms\n           - MaterializeTupleTime(*): 0.000ns\n           - ScannerThreadsSysTime: 0.000ns\n           - ScannerThreadsUserTime: 819.000us\n         - ScannerThreadsVoluntaryContextSwitches: 9 (9)\n         - TotalRawHdfsReadTime(*): 0.000ns\n         - TotalReadThroughput: 0.00 /sec\n    Fragment F00:\n      Instance 1a48b5796f8f07f5:49ba9e6b00000001 (host=nightly512-unsecure-2.gce.cloudera.com:22000):(Total: 241.020ms, non-child: 0.000ns, % non-child: 0.00%)\n        Hdfs split stats (<volume id>:<# splits>/<split lengths>): 0:1/15.44 KB \n         - AverageThreadTokens: 0.00 \n         - BloomFilterBytes: 0\n         - PeakMemoryUsage: 63.09 KB (64608)\n         - PerHostPeakMemUsage: 71.09 KB (72800)\n         - RowsProduced: 53 (53)\n         - TotalNetworkReceiveTime: 0.000ns\n         - TotalNetworkSendTime: 0.000ns\n         - TotalStorageWaitTime: 175.014ms\n         - TotalThreadsInvoluntaryContextSwitches: 2 (2)\n         - TotalThreadsTotalWallClockTime: 378.032ms\n           - TotalThreadsSysTime: 1.998ms\n           - TotalThreadsUserTime: 24.546ms\n         - TotalThreadsVoluntaryContextSwitches: 13 (13)\n        Fragment Instance Lifecycle Timings:\n           - ExecTime: 176.015ms\n             - ExecTreeExecTime: 176.015ms\n           - OpenTime: 26.002ms\n             - ExecTreeOpenTime: 1.000ms\n           - PrepareTime: 39.003ms\n             - ExecTreePrepareTime: 19.001ms\n        DataStreamSender (dst_id=1):\n           - BytesSent: 1.54 KB (1578)\n           - NetworkThroughput(*): 0.00 /sec\n           - OverallThroughput: 0.00 /sec\n           - PeakMemoryUsage: 6.09 KB (6240)\n           - RowsReturned: 53 (53)\n           - SerializeBatchTime: 0.000ns\n           - TransmitDataRPCTime: 0.000ns\n           - UncompressedRowBatchSize: 2.05 KB (2098)\n        CodeGen:(Total: 43.003ms, non-child: 43.003ms, % non-child: 100.00%)\n           - CodegenTime: 1.000ms\n           - CompileTime: 13.001ms\n           - LoadTime: 0.000ns\n           - ModuleBitcodeSize: 1.98 MB (2077616)\n           - NumFunctions: 5 (5)\n           - NumInstructions: 98 (98)\n           - OptimizationTime: 11.000ms\n           - PeakMemoryUsage: 49.00 KB (50176)\n           - PrepareTime: 18.001ms\n        HDFS_SCAN_NODE (id=0):(Total: 215.018ms, non-child: 215.018ms, % non-child: 100.00%)\n          Hdfs split stats (<volume id>:<# splits>/<split lengths>): 0:1/15.44 KB \n          ExecOption: PARQUET Codegen Enabled, Codegen enabled: 1 out of 1\n          Hdfs Read Thread Concurrency Bucket: 0:0% 1:0% 2:0% 3:0% 4:0% \n          File Formats: PARQUET/NONE:2 \n           - FooterProcessingTime: (Avg: 168.014ms ; Min: 168.014ms ; Max: 168.014ms ; Number of samples: 1)\n           - AverageHdfsReadThreadConcurrency: 0.00 \n           - AverageScannerThreadConcurrency: 0.00 \n           - BytesRead: 16.71 KB (17111)\n           - BytesReadDataNodeCache: 0\n           - BytesReadLocal: 16.71 KB (17111)\n           - BytesReadRemoteUnexpected: 0\n           - BytesReadShortCircuit: 16.71 KB (17111)\n           - DecompressionTime: 0.000ns\n           - MaxCompressedTextFileLength: 0\n           - NumColumns: 2 (2)\n           - NumDictFilteredRowGroups: 0 (0)\n           - NumDisksAccessed: 1 (1)\n           - NumRowGroups: 1 (1)\n           - NumScannerThreadsStarted: 1 (1)\n           - NumScannersWithNoReads: 0 (0)\n           - NumStatsFilteredRowGroups: 0 (0)\n           - PeakMemoryUsage: 45.02 KB (46101)\n           - PerReadThreadRawHdfsThroughput: 0.00 /sec\n           - RemoteScanRanges: 0 (0)\n           - RowBatchQueueGetWaitTime: 176.015ms\n           - RowBatchQueuePutWaitTime: 0.000ns\n           - RowsRead: 53 (53)\n           - RowsReturned: 53 (53)\n           - RowsReturnedRate: 246.00 /sec\n           - ScanRangesComplete: 1 (1)\n           - ScannerThreadsInvoluntaryContextSwitches: 0 (0)\n           - ScannerThreadsTotalWallClockTime: 176.015ms\n             - MaterializeTupleTime(*): 0.000ns\n             - ScannerThreadsSysTime: 0.000ns\n             - ScannerThreadsUserTime: 819.000us\n           - ScannerThreadsVoluntaryContextSwitches: 9 (9)\n           - TotalRawHdfsReadTime(*): 0.000ns\n           - TotalReadThroughput: 0.00 /sec\n', u'query_id': u'1a48b5796f8f07f5:49ba9e6b00000000', u'__common__': {u'navbar': [{u'link': u'/backends', u'title': u'/backends'}, {u'link': u'/catalog', u'title': u'/catalog'}, {u'link': u'/hadoop-varz', u'title': u'/hadoop-varz'}, {u'link': u'/log_level', u'title': u'/log_level'}, {u'link': u'/logs', u'title': u'/logs'}, {u'link': u'/memz', u'title': u'/memz'}, {u'link': u'/metrics', u'title': u'/metrics'}, {u'link': u'/queries', u'title': u'/queries'}, {u'link': u'/rpcz', u'title': u'/rpcz'}, {u'link': u'/sessions', u'title': u'/sessions'}, {u'link': u'/threadz', u'title': u'/threadz'}, {u'link': u'/varz', u'title': u'/varz'}], u'process-name': u'impalad'}},
    '8a46a8865624698f:b80b211500000000': {u'profile': u'Query (id=d424420e0c44ab9:c637ac2900000000):\n  Summary:\n    Session ID: 3348564c97187569:1c17ce45bdfbf0b2\n    Session Type: HIVESERVER2\n    HiveServer2 Protocol Version: V6\n    Start Time: 2017-10-26 11:20:11.971764000\n    End Time: 2017-10-26 11:23:11.429110000\n    Query Type: QUERY\n    Query State: FINISHED\n    Query Status: OK\n    Impala Version: impalad version 2.9.0-cdh5.12.1 RELEASE (build 6dacae08a283a36bb932335ae0c046977e2474e8)\n    User: admin\n    Connected User: admin\n    Delegated User: \n    Network Address: 10.16.2.226:63745\n    Default Db: default\n    Sql Statement: SELECT sample_07.description, sample_07.salary\r\nFROM\r\n  sample_07\r\nWHERE\r\n( sample_07.salary > 100000)\r\nORDER BY sample_07.salary DESC\r\nLIMIT 1000\n    Coordinator: nightly512-unsecure-2.gce.cloudera.com:22000\n    Query Options (set by configuration): QUERY_TIMEOUT_S=600\n    Query Options (set by configuration and planner): QUERY_TIMEOUT_S=600,MT_DOP=0\n    Plan: \n----------------\nPer-Host Resource Reservation: Memory=0B\nPer-Host Resource Estimates: Memory=32.00MB\nWARNING: The following tables have potentially corrupt table statistics.\nDrop and re-compute statistics to resolve this problem.\ndefault.sample_07\nWARNING: The following tables are missing relevant table and/or column statistics.\ndefault.sample_07\n\nF01:PLAN FRAGMENT [UNPARTITIONED] hosts=1 instances=1\nPLAN-ROOT SINK\n|  mem-estimate=0B mem-reservation=0B\n|\n02:MERGING-EXCHANGE [UNPARTITIONED]\n|  order by: salary DESC\n|  limit: 1000\n|  mem-estimate=0B mem-reservation=0B\n|  tuple-ids=1 row-size=19B cardinality=0\n|\nF00:PLAN FRAGMENT [RANDOM] hosts=1 instances=1\n01:TOP-N [LIMIT=1000]\n|  order by: salary DESC\n|  mem-estimate=0B mem-reservation=0B\n|  tuple-ids=1 row-size=19B cardinality=0\n|\n00:SCAN HDFS [default.sample_07, RANDOM]\n   partitions=1/1 files=1 size=44.98KB\n   predicates: (sample_07.salary > 100000)\n   table stats: 0 rows total\n   column stats: unavailable\n   parquet dictionary predicates: (sample_07.salary > 100000)\n   mem-estimate=32.00MB mem-reservation=0B\n   tuple-ids=0 row-size=19B cardinality=0\n----------------\n    Estimated Per-Host Mem: 33554432\n    Per-Host Memory Reservation: 0\n    Tables Missing Stats: default.sample_07\n    Tables With Corrupt Table Stats: default.sample_07\n    Request Pool: root.admin\n    Admission result: Admitted immediately\n    ExecSummary: \nOperator              #Hosts   Avg Time   Max Time  #Rows  Est. #Rows   Peak Mem  Est. Peak Mem  Detail            \n-------------------------------------------------------------------------------------------------------------------\n02:MERGING-EXCHANGE        1    0.000ns    0.000ns     28           0          0              0  UNPARTITIONED     \n01:TOP-N                   1    0.000ns    0.000ns     28           0   80.00 KB              0                    \n00:SCAN HDFS               1  250.020ms  250.020ms     28           0  173.00 KB       32.00 MB  default.sample_07 \n    Errors: \n    Planner Timeline: 3s275ms\n       - Metadata load started: 11.586ms (11.586ms)\n       - Metadata load finished: 3s248ms (3s236ms)\n       - Analysis finished: 3s254ms (6.431ms)\n       - Equivalence classes computed: 3s255ms (335.173us)\n       - Single node plan created: 3s267ms (12.443ms)\n       - Runtime filters computed: 3s267ms (92.906us)\n       - Distributed plan created: 3s267ms (223.487us)\n       - Lineage info computed: 3s268ms (348.540us)\n       - Planning finished: 3s275ms (7.378ms)\n    Query Timeline: 2m59s\n       - Query submitted: 0.000ns (0.000ns)\n       - Planning finished: 3s278ms (3s278ms)\n       - Submit for admission: 3s279ms (1.000ms)\n       - Completed admission: 3s279ms (0.000ns)\n       - Ready to start on 2 backends: 3s279ms (0.000ns)\n       - All 2 execution backends (2 fragment instances) started: 3s331ms (52.004ms)\n       - Rows available: 3s781ms (450.038ms)\n       - First row fetched: 5s232ms (1s451ms)\n       - Unregister query: 2m59s (2m54s)\n     - ComputeScanRangeAssignmentTimer: 0.000ns\n  ImpalaServer:\n     - ClientFetchWaitTimer: 2m55s\n     - RowMaterializationTimer: 0.000ns\n  Execution Profile d424420e0c44ab9:c637ac2900000000:(Total: 502.042ms, non-child: 0.000ns, % non-child: 0.00%)\n    Number of filters: 0\n    Filter routing table: \n ID  Src. Node  Tgt. Node(s)  Target type  Partition filter  Pending (Expected)  First arrived  Completed   Enabled\n-------------------------------------------------------------------------------------------------------------------\n\n    Backend startup latencies: Count: 2, min / max: 1ms / 52ms, 25th %-ile: 1ms, 50th %-ile: 1ms, 75th %-ile: 52ms, 90th %-ile: 52ms, 95th %-ile: 52ms, 99.9th %-ile: 52ms\n    Per Node Peak Memory Usage: nightly512-unsecure-2.gce.cloudera.com:22000(255.00 KB) nightly512-unsecure-3.gce.cloudera.com:22000(937.09 KB) \n     - FiltersReceived: 0 (0)\n     - FinalizationTimer: 0.000ns\n    Averaged Fragment F01:(Total: 1s952ms, non-child: 1s452ms, % non-child: 74.39%)\n      split sizes:  min: 0, max: 0, avg: 0, stddev: 0\n      completion times: min:1s952ms  max:1s952ms  mean: 1s952ms  stddev:0.000ns\n      execution rates: min:0.00 /sec  max:0.00 /sec  mean:0.00 /sec  stddev:0.00 /sec\n      num instances: 1\n       - AverageThreadTokens: 0.00 \n       - BloomFilterBytes: 0\n       - PeakMemoryUsage: 255.00 KB (261120)\n       - PerHostPeakMemUsage: 255.00 KB (261120)\n       - RowsProduced: 28 (28)\n       - TotalNetworkReceiveTime: 0.000ns\n       - TotalNetworkSendTime: 0.000ns\n       - TotalStorageWaitTime: 0.000ns\n       - TotalThreadsInvoluntaryContextSwitches: 1 (1)\n       - TotalThreadsTotalWallClockTime: 1s934ms\n         - TotalThreadsSysTime: 980.000us\n         - TotalThreadsUserTime: 28.421ms\n       - TotalThreadsVoluntaryContextSwitches: 3 (3)\n      Fragment Instance Lifecycle Timings:\n         - ExecTime: 1s451ms\n           - ExecTreeExecTime: 0.000ns\n         - OpenTime: 483.041ms\n           - ExecTreeOpenTime: 452.038ms\n         - PrepareTime: 18.001ms\n           - ExecTreePrepareTime: 0.000ns\n      BlockMgr:\n         - BlockWritesOutstanding: 0 (0)\n         - BlocksCreated: 0 (0)\n         - BlocksRecycled: 0 (0)\n         - BufferedPins: 0 (0)\n         - MaxBlockSize: 8.00 MB (8388608)\n         - MemoryLimit: 16.33 GB (17534060544)\n         - PeakMemoryUsage: 0\n         - ScratchBytesRead: 0\n         - ScratchBytesWritten: 0\n         - ScratchFileUsedBytes: 0\n         - ScratchReads: 0 (0)\n         - ScratchWrites: 0 (0)\n         - TotalBufferWaitTime: 0.000ns\n         - TotalEncryptionTime: 0.000ns\n         - TotalReadBlockTime: 0.000ns\n      PLAN_ROOT_SINK:\n         - PeakMemoryUsage: 0\n      CodeGen:(Total: 48.004ms, non-child: 48.004ms, % non-child: 100.00%)\n         - CodegenTime: 0.000ns\n         - CompileTime: 3.000ms\n         - LoadTime: 0.000ns\n         - ModuleBitcodeSize: 1.98 MB (2077616)\n         - NumFunctions: 27 (27)\n         - NumInstructions: 494 (494)\n         - OptimizationTime: 26.002ms\n         - PeakMemoryUsage: 247.00 KB (252928)\n         - PrepareTime: 18.001ms\n      EXCHANGE_NODE (id=2):(Total: 452.038ms, non-child: 452.038ms, % non-child: 100.00%)\n         - BytesReceived: 923.00 B (923)\n         - ConvertRowBatchTime: 0.000ns\n         - DeserializeRowBatchTimer: 0.000ns\n         - FirstBatchArrivalWaitTime: 452.038ms\n         - MergeGetNext: 0.000ns\n         - MergeGetNextBatch: 0.000ns\n         - PeakMemoryUsage: 0\n         - RowsReturned: 28 (28)\n         - RowsReturnedRate: 61.00 /sec\n         - SendersBlockedTimer: 0.000ns\n         - SendersBlockedTotalTimer(*): 0.000ns\n    Coordinator Fragment F01:\n      Instance d424420e0c44ab9:c637ac2900000000 (host=nightly512-unsecure-2.gce.cloudera.com:22000):(Total: 1s952ms, non-child: 1s452ms, % non-child: 74.39%)\n        MemoryUsage(500.000ms): 8.09 KB, 12.09 KB, 12.09 KB, 12.09 KB\n         - AverageThreadTokens: 0.00 \n         - BloomFilterBytes: 0\n         - PeakMemoryUsage: 255.00 KB (261120)\n         - PerHostPeakMemUsage: 255.00 KB (261120)\n         - RowsProduced: 28 (28)\n         - TotalNetworkReceiveTime: 0.000ns\n         - TotalNetworkSendTime: 0.000ns\n         - TotalStorageWaitTime: 0.000ns\n         - TotalThreadsInvoluntaryContextSwitches: 1 (1)\n         - TotalThreadsTotalWallClockTime: 1s934ms\n           - TotalThreadsSysTime: 980.000us\n           - TotalThreadsUserTime: 28.421ms\n         - TotalThreadsVoluntaryContextSwitches: 3 (3)\n        Fragment Instance Lifecycle Timings:\n           - ExecTime: 1s451ms\n             - ExecTreeExecTime: 0.000ns\n           - OpenTime: 483.041ms\n             - ExecTreeOpenTime: 452.038ms\n           - PrepareTime: 18.001ms\n             - ExecTreePrepareTime: 0.000ns\n        BlockMgr:\n           - BlockWritesOutstanding: 0 (0)\n           - BlocksCreated: 0 (0)\n           - BlocksRecycled: 0 (0)\n           - BufferedPins: 0 (0)\n           - MaxBlockSize: 8.00 MB (8388608)\n           - MemoryLimit: 16.33 GB (17534060544)\n           - PeakMemoryUsage: 0\n           - ScratchBytesRead: 0\n           - ScratchBytesWritten: 0\n           - ScratchFileUsedBytes: 0\n           - ScratchReads: 0 (0)\n           - ScratchWrites: 0 (0)\n           - TotalBufferWaitTime: 0.000ns\n           - TotalEncryptionTime: 0.000ns\n           - TotalReadBlockTime: 0.000ns\n        PLAN_ROOT_SINK:\n           - PeakMemoryUsage: 0\n        CodeGen:(Total: 48.004ms, non-child: 48.004ms, % non-child: 100.00%)\n           - CodegenTime: 0.000ns\n           - CompileTime: 3.000ms\n           - LoadTime: 0.000ns\n           - ModuleBitcodeSize: 1.98 MB (2077616)\n           - NumFunctions: 27 (27)\n           - NumInstructions: 494 (494)\n           - OptimizationTime: 26.002ms\n           - PeakMemoryUsage: 247.00 KB (252928)\n           - PrepareTime: 18.001ms\n        EXCHANGE_NODE (id=2):(Total: 452.038ms, non-child: 0.000ns, % non-child: 0.00%)\n          ExecOption: Codegen Enabled\n          BytesReceived(500.000ms): 0, 923.00 B, 923.00 B, 923.00 B\n           - BytesReceived: 923.00 B (923)\n           - ConvertRowBatchTime: 0.000ns\n           - DeserializeRowBatchTimer: 0.000ns\n           - FirstBatchArrivalWaitTime: 452.038ms\n           - MergeGetNext: 0.000ns\n           - MergeGetNextBatch: 0.000ns\n           - PeakMemoryUsage: 0\n           - RowsReturned: 28 (28)\n           - RowsReturnedRate: 61.00 /sec\n           - SendersBlockedTimer: 0.000ns\n           - SendersBlockedTotalTimer(*): 0.000ns\n    Averaged Fragment F00:(Total: 450.037ms, non-child: 55.004ms, % non-child: 12.22%)\n      split sizes:  min: 44.98 KB, max: 44.98 KB, avg: 44.98 KB, stddev: 0\n      completion times: min:450.038ms  max:450.038ms  mean: 450.038ms  stddev:0.000ns\n      execution rates: min:99.94 KB/sec  max:99.94 KB/sec  mean:99.94 KB/sec  stddev:0.68 B/sec\n      num instances: 1\n       - AverageThreadTokens: 2.00 \n       - BloomFilterBytes: 0\n       - PeakMemoryUsage: 937.09 KB (959584)\n       - PerHostPeakMemUsage: 937.09 KB (959584)\n       - RowsProduced: 28 (28)\n       - TotalNetworkReceiveTime: 0.000ns\n       - TotalNetworkSendTime: 50.004ms\n       - TotalStorageWaitTime: 180.014ms\n       - TotalThreadsInvoluntaryContextSwitches: 1 (1)\n       - TotalThreadsTotalWallClockTime: 570.046ms\n         - TotalThreadsSysTime: 3.300ms\n         - TotalThreadsUserTime: 157.428ms\n       - TotalThreadsVoluntaryContextSwitches: 9 (9)\n      Fragment Instance Lifecycle Timings:\n         - ExecTime: 51.004ms\n           - ExecTreeExecTime: 0.000ns\n         - OpenTime: 339.027ms\n           - ExecTreeOpenTime: 180.014ms\n         - PrepareTime: 60.004ms\n           - ExecTreePrepareTime: 35.002ms\n      BlockMgr:\n         - BlockWritesOutstanding: 0 (0)\n         - BlocksCreated: 0 (0)\n         - BlocksRecycled: 0 (0)\n         - BufferedPins: 0 (0)\n         - MaxBlockSize: 8.00 MB (8388608)\n         - MemoryLimit: 16.33 GB (17534060544)\n         - PeakMemoryUsage: 0\n         - ScratchBytesRead: 0\n         - ScratchBytesWritten: 0\n         - ScratchFileUsedBytes: 0\n         - ScratchReads: 0 (0)\n         - ScratchWrites: 0 (0)\n         - TotalBufferWaitTime: 0.000ns\n         - TotalEncryptionTime: 0.000ns\n         - TotalReadBlockTime: 0.000ns\n      DataStreamSender (dst_id=2):\n         - BytesSent: 923.00 B (923)\n         - NetworkThroughput(*): 0.00 /sec\n         - OverallThroughput: 0.00 /sec\n         - PeakMemoryUsage: 6.09 KB (6240)\n         - RowsReturned: 28 (28)\n         - SerializeBatchTime: 0.000ns\n         - TransmitDataRPCTime: 0.000ns\n         - UncompressedRowBatchSize: 1.30 KB (1333)\n      CodeGen:(Total: 180.014ms, non-child: 180.014ms, % non-child: 100.00%)\n         - CodegenTime: 3.000ms\n         - CompileTime: 42.003ms\n         - LoadTime: 0.000ns\n         - ModuleBitcodeSize: 1.98 MB (2077616)\n         - NumFunctions: 94 (94)\n         - NumInstructions: 1.85K (1846)\n         - OptimizationTime: 116.009ms\n         - PeakMemoryUsage: 923.00 KB (945152)\n         - PrepareTime: 21.001ms\n      SORT_NODE (id=1):(Total: 215.017ms, non-child: 0.000ns, % non-child: 0.00%)\n         - InsertBatchTime: 0.000ns\n         - PeakMemoryUsage: 80.00 KB (81920)\n         - RowsReturned: 28 (28)\n         - RowsReturnedRate: 130.00 /sec\n      HDFS_SCAN_NODE (id=0):(Total: 250.020ms, non-child: 250.020ms, % non-child: 100.00%)\n         - AverageHdfsReadThreadConcurrency: 0.00 \n         - AverageScannerThreadConcurrency: 1.00 \n         - BytesRead: 44.98 KB (46055)\n         - BytesReadDataNodeCache: 0\n         - BytesReadLocal: 44.98 KB (46055)\n         - BytesReadRemoteUnexpected: 0\n         - BytesReadShortCircuit: 44.98 KB (46055)\n         - DecompressionTime: 0.000ns\n         - MaxCompressedTextFileLength: 0\n         - NumDisksAccessed: 1 (1)\n         - NumScannerThreadsStarted: 1 (1)\n         - PeakMemoryUsage: 173.00 KB (177152)\n         - PerReadThreadRawHdfsThroughput: 0.00 /sec\n         - RemoteScanRanges: 0 (0)\n         - RowBatchQueueGetWaitTime: 180.014ms\n         - RowBatchQueuePutWaitTime: 0.000ns\n         - RowsRead: 823 (823)\n         - RowsReturned: 28 (28)\n         - RowsReturnedRate: 111.00 /sec\n         - ScanRangesComplete: 1 (1)\n         - ScannerThreadsInvoluntaryContextSwitches: 0 (0)\n         - ScannerThreadsTotalWallClockTime: 180.014ms\n           - DelimiterParseTime: 0.000ns\n           - MaterializeTupleTime(*): 0.000ns\n           - ScannerThreadsSysTime: 324.000us\n           - ScannerThreadsUserTime: 0.000ns\n         - ScannerThreadsVoluntaryContextSwitches: 4 (4)\n         - TotalRawHdfsReadTime(*): 0.000ns\n         - TotalReadThroughput: 0.00 /sec\n    Fragment F00:\n      Instance d424420e0c44ab9:c637ac2900000001 (host=nightly512-unsecure-3.gce.cloudera.com:22000):(Total: 450.037ms, non-child: 55.004ms, % non-child: 12.22%)\n        Hdfs split stats (<volume id>:<# splits>/<split lengths>): 0:1/44.98 KB \n        MemoryUsage(500.000ms): 130.54 KB\n        ThreadUsage(500.000ms): 2\n         - AverageThreadTokens: 2.00 \n         - BloomFilterBytes: 0\n         - PeakMemoryUsage: 937.09 KB (959584)\n         - PerHostPeakMemUsage: 937.09 KB (959584)\n         - RowsProduced: 28 (28)\n         - TotalNetworkReceiveTime: 0.000ns\n         - TotalNetworkSendTime: 50.004ms\n         - TotalStorageWaitTime: 180.014ms\n         - TotalThreadsInvoluntaryContextSwitches: 1 (1)\n         - TotalThreadsTotalWallClockTime: 570.046ms\n           - TotalThreadsSysTime: 3.300ms\n           - TotalThreadsUserTime: 157.428ms\n         - TotalThreadsVoluntaryContextSwitches: 9 (9)\n        Fragment Instance Lifecycle Timings:\n           - ExecTime: 51.004ms\n             - ExecTreeExecTime: 0.000ns\n           - OpenTime: 339.027ms\n             - ExecTreeOpenTime: 180.014ms\n           - PrepareTime: 60.004ms\n             - ExecTreePrepareTime: 35.002ms\n        BlockMgr:\n           - BlockWritesOutstanding: 0 (0)\n           - BlocksCreated: 0 (0)\n           - BlocksRecycled: 0 (0)\n           - BufferedPins: 0 (0)\n           - MaxBlockSize: 8.00 MB (8388608)\n           - MemoryLimit: 16.33 GB (17534060544)\n           - PeakMemoryUsage: 0\n           - ScratchBytesRead: 0\n           - ScratchBytesWritten: 0\n           - ScratchFileUsedBytes: 0\n           - ScratchReads: 0 (0)\n           - ScratchWrites: 0 (0)\n           - TotalBufferWaitTime: 0.000ns\n           - TotalEncryptionTime: 0.000ns\n           - TotalReadBlockTime: 0.000ns\n        DataStreamSender (dst_id=2):\n           - BytesSent: 923.00 B (923)\n           - NetworkThroughput(*): 0.00 /sec\n           - OverallThroughput: 0.00 /sec\n           - PeakMemoryUsage: 6.09 KB (6240)\n           - RowsReturned: 28 (28)\n           - SerializeBatchTime: 0.000ns\n           - TransmitDataRPCTime: 0.000ns\n           - UncompressedRowBatchSize: 1.30 KB (1333)\n        CodeGen:(Total: 180.014ms, non-child: 180.014ms, % non-child: 100.00%)\n           - CodegenTime: 3.000ms\n           - CompileTime: 42.003ms\n           - LoadTime: 0.000ns\n           - ModuleBitcodeSize: 1.98 MB (2077616)\n           - NumFunctions: 94 (94)\n           - NumInstructions: 1.85K (1846)\n           - OptimizationTime: 116.009ms\n           - PeakMemoryUsage: 923.00 KB (945152)\n           - PrepareTime: 21.001ms\n        SORT_NODE (id=1):(Total: 215.017ms, non-child: 0.000ns, % non-child: 0.00%)\n          ExecOption: Codegen Enabled\n           - InsertBatchTime: 0.000ns\n           - PeakMemoryUsage: 80.00 KB (81920)\n           - RowsReturned: 28 (28)\n           - RowsReturnedRate: 130.00 /sec\n        HDFS_SCAN_NODE (id=0):(Total: 250.020ms, non-child: 250.020ms, % non-child: 100.00%)\n          Hdfs split stats (<volume id>:<# splits>/<split lengths>): 0:1/44.98 KB \n          ExecOption: TEXT Codegen Enabled, Codegen enabled: 1 out of 1\n          Hdfs Read Thread Concurrency Bucket: 0:100% 1:0% 2:0% 3:0% 4:0% \n          File Formats: TEXT/NONE:1 \n          BytesRead(500.000ms): 0\n           - AverageHdfsReadThreadConcurrency: 0.00 \n           - AverageScannerThreadConcurrency: 1.00 \n           - BytesRead: 44.98 KB (46055)\n           - BytesReadDataNodeCache: 0\n           - BytesReadLocal: 44.98 KB (46055)\n           - BytesReadRemoteUnexpected: 0\n           - BytesReadShortCircuit: 44.98 KB (46055)\n           - DecompressionTime: 0.000ns\n           - MaxCompressedTextFileLength: 0\n           - NumDisksAccessed: 1 (1)\n           - NumScannerThreadsStarted: 1 (1)\n           - PeakMemoryUsage: 173.00 KB (177152)\n           - PerReadThreadRawHdfsThroughput: 0.00 /sec\n           - RemoteScanRanges: 0 (0)\n           - RowBatchQueueGetWaitTime: 180.014ms\n           - RowBatchQueuePutWaitTime: 0.000ns\n           - RowsRead: 823 (823)\n           - RowsReturned: 28 (28)\n           - RowsReturnedRate: 111.00 /sec\n           - ScanRangesComplete: 1 (1)\n           - ScannerThreadsInvoluntaryContextSwitches: 0 (0)\n           - ScannerThreadsTotalWallClockTime: 180.014ms\n             - DelimiterParseTime: 0.000ns\n             - MaterializeTupleTime(*): 0.000ns\n             - ScannerThreadsSysTime: 324.000us\n             - ScannerThreadsUserTime: 0.000ns\n           - ScannerThreadsVoluntaryContextSwitches: 4 (4)\n           - TotalRawHdfsReadTime(*): 0.000ns\n           - TotalReadThroughput: 0.00 /sec\n', u'query_id': u'd424420e0c44ab9:c637ac2900000000', u'__common__': {u'navbar': [{u'link': u'/backends', u'title': u'/backends'}, {u'link': u'/catalog', u'title': u'/catalog'}, {u'link': u'/hadoop-varz', u'title': u'/hadoop-varz'}, {u'link': u'/log_level', u'title': u'/log_level'}, {u'link': u'/logs', u'title': u'/logs'}, {u'link': u'/memz', u'title': u'/memz'}, {u'link': u'/metrics', u'title': u'/metrics'}, {u'link': u'/queries', u'title': u'/queries'}, {u'link': u'/rpcz', u'title': u'/rpcz'}, {u'link': u'/sessions', u'title': u'/sessions'}, {u'link': u'/threadz', u'title': u'/threadz'}, {u'link': u'/varz', u'title': u'/varz'}], u'process-name': u'impalad'}}
  }
  MEMORY = {
    '4d497267f34ff17d:817bdfb500000000': {u'query_id': u'1a48b5796f8f07f5:49ba9e6b00000000', u'__common__': {u'navbar': [{u'link': u'/backends', u'title': u'/backends'}, {u'link': u'/catalog', u'title': u'/catalog'}, {u'link': u'/hadoop-varz', u'title': u'/hadoop-varz'}, {u'link': u'/log_level', u'title': u'/log_level'}, {u'link': u'/logs', u'title': u'/logs'}, {u'link': u'/memz', u'title': u'/memz'}, {u'link': u'/metrics', u'title': u'/metrics'}, {u'link': u'/queries', u'title': u'/queries'}, {u'link': u'/rpcz', u'title': u'/rpcz'}, {u'link': u'/sessions', u'title': u'/sessions'}, {u'link': u'/threadz', u'title': u'/threadz'}, {u'link': u'/varz', u'title': u'/varz'}], u'process-name': u'impalad'}, u'mem_usage': u'The query is finished, current memory consumption is not available.'},
    '8a46a8865624698f:b80b211500000000': {u'query_id': u'd424420e0c44ab9:c637ac2900000000', u'__common__': {u'navbar': [{u'link': u'/backends', u'title': u'/backends'}, {u'link': u'/catalog', u'title': u'/catalog'}, {u'link': u'/hadoop-varz', u'title': u'/hadoop-varz'}, {u'link': u'/log_level', u'title': u'/log_level'}, {u'link': u'/logs', u'title': u'/logs'}, {u'link': u'/memz', u'title': u'/memz'}, {u'link': u'/metrics', u'title': u'/metrics'}, {u'link': u'/queries', u'title': u'/queries'}, {u'link': u'/rpcz', u'title': u'/rpcz'}, {u'link': u'/sessions', u'title': u'/sessions'}, {u'link': u'/threadz', u'title': u'/threadz'}, {u'link': u'/varz', u'title': u'/varz'}], u'process-name': u'impalad'}, u'mem_usage': u'The query is finished, current memory consumption is not available.'}
  }
  def __init__(self, url):
    self.url = url

  def get_queries(self, **kwargs):
    return {
      'completed_queries': [
        MockImpalaQueryApi.APPS['4d497267f34ff17d:817bdfb500000000'],
        MockImpalaQueryApi.APPS['8a46a8865624698f:b80b211500000000']
      ],
      'in_flight_queries': [],
      'num_in_flight_queries':0,
      'num_executing_queries': 0,
      'num_waiting_queries': 0
    }

  def get_query(self, query_id):
    return MockImpalaQueryApi.PLAN[query_id]

  def get_query_profile(self, query_id):
    return MockImpalaQueryApi.PROFILE[query_id]

  def get_query_memory(self, query_id):
    return MockImpalaQueryApi.MEMORY[query_id]

  def kill(self, query_id):
    pass


class MockMapreduce2Api(object):
  """
  MockMapreduceApi and HistoryServerApi are very similar and inherit from it.
  """

  def __init__(self, mr_url=None): pass

  def tasks(self, job_id):
    return {
      u'tasks': {
        u'task': [{
            u'finishTime': 1357153330271, u'successfulAttempt': u'attempt_1356251510842_0062_m_000000_0', u'elapsedTime': 1901, u'state': u'SUCCEEDED',
            u'startTime': 1357153328370, u'progress': 100.0, u'type': u'MAP', u'id': u'task_1356251510842_0062_m_000000'},
                  {
            u'finishTime': 0, u'successfulAttempt': u'', u'elapsedTime': 0, u'state': u'SCHEDULED', u'startTime': 1357153326322, u'progress': 0.0,
            u'type': u'REDUCE', u'id': u'task_1356251510842_0062_r_000000'}
        ]
      }
    }

  def conf(self, job_id):
    return {
      "conf" : {
        "path" : "hdfs://host.domain.com:9000/user/user1/.staging/job_1326232085508_0004/job.xml",
        "property" : [
           {
              "name" : "dfs.datanode.data.dir",
              "value" : "/home/hadoop/hdfs/data",
           }, {
              "name" : "mapreduce.job.acl-modify-job",
              "value" : "test",
           }, {
              "name" : "mapreduce.job.acl-view-job",
              "value" : "test,test2",
           }
         ]
      }
    }

  def job_attempts(self, job_id):
    return {
       "jobAttempts" : {
          "jobAttempt" : [
             {
                "nodeId" : "host.domain.com:8041",
                "nodeHttpAddress" : "host.domain.com:8042",
                "startTime" : 1326238773493,
                "id" : 1,
                "logsLink" : "http://host.domain.com:8042/node/containerlogs/container_1326232085508_0004_01_000001",
                "containerId" : "container_1326232085508_0004_01_000001"
             }
          ]
       }
    }

  def task_attempts(self, job_id, task_id):
    return {
       "taskAttempts" : {
          "taskAttempt" : [
             {
                "elapsedMergeTime" : 47,
                "shuffleFinishTime" : 1326238780052,
                "assignedContainerId" : "container_1326232085508_0004_01_000003",
                "progress" : 100,
                "elapsedTime" : 0,
                "state" : "RUNNING",
                "elapsedShuffleTime" : 2592,
                "mergeFinishTime" : 1326238780099,
                "rack" : "/98.139.92.0",
                "elapsedReduceTime" : 0,
                "nodeHttpAddress" : "host.domain.com:8042",
                "type" : "REDUCE",
                "startTime" : 1326238777460,
                "id" : "attempt_1326232085508_4_4_r_0_0",
                "finishTime" : 0
             }
          ]
       }
    }

  def counters(self, job_id):
    return {
       "jobCounters" : {
          "id" : "job_1326232085508_4_4",
          "counterGroup" : [
             {
                "counterGroupName" : "org.apache.hadoop.mapreduce.lib.input.FileInputFormatCounter",
                "counter" : [
                   {
                      "reduceCounterValue" : 0,
                      "mapCounterValue" : 0,
                      "totalCounterValue" : 0,
                      "name" : "BYTES_READ"
                   }
                ]
             },
             {
                "counterGroupName" : "org.apache.hadoop.mapreduce.lib.output.FileOutputFormatCounter",
                "counter" : [
                   {
                      "reduceCounterValue" : 0,
                      "mapCounterValue" : 0,
                      "totalCounterValue" : 0,
                      "name" : "BYTES_WRITTEN"
                   }
                ]
             }
          ]
       }
    }

  def kill(self, job_id):
    job_id = job_id.replace('job', 'application')
    MockResourceManagerApi.APPS[job_id]['state'] = 'KILLED'
    return {}


class MockMapreduceApi(MockMapreduce2Api):
  def job(self, user, job_id):
    if '1356251510842_0009' not in job_id:
      job = {
          u'job': {
              u'reducesCompleted': 0, u'mapsRunning': 1, u'id': u'job_1356251510842_0054', u'successfulReduceAttempts': 0, u'successfulMapAttempts': 0,
              u'uberized': False, u'reducesTotal': 1, u'elapsedTime': 3426, u'mapsPending': 0, u'state': u'RUNNING', u'failedReduceAttempts': 0,
              u'mapsCompleted': 0, u'killedMapAttempts': 0, u'killedReduceAttempts': 0, u'runningReduceAttempts': 0, u'failedMapAttempts': 0, u'mapsTotal': 1,
              u'user': u'test', u'startTime': 1357152972886, u'reducesPending': 1, u'reduceProgress': 0.0, u'finishTime': 0,
              u'name': u'select avg(salary) from sample_07(Stage-1)', u'reducesRunning': 0, u'newMapAttempts': 0, u'diagnostics': u'', u'mapProgress': 0.0,
              u'runningMapAttempts': 1, u'newReduceAttempts': 1,
              # Does not seems to exist in API, we actually skip it in case.
              "acls" : [{
                  "value" : "test",
                  "name" : "mapreduce.job.acl-modify-job"
               }, {
                  "value" : "test",
                  "name" : "mapreduce.job.acl-view-job"
               }
              ],
          }
      }
      job['job']['id'] = job_id
      return job

class MockSparkHistoryApi(SparkHistoryServerApi):
  def __init__(self):
    self.APPS = [{
        "id": "application_1513618343677_0018",
        "name": "Sleep15minPySpark",
        "attempts": [ {
          "attemptId": "1",
          "startTime": "2017-12-20T20:25:19.672GMT",
          "endTime": "2017-12-20T20:40:43.768GMT",
          "sparkUser": "test",
          "completed": True
      }]
    }, {
        "id": "application_1513618343677_0020",
        "name": "Sleep15minPySpark",
        "attempts": [ {
          "attemptId": "2",
          "startTime": "2017-12-24T03:19:29.993GMT",
          "endTime": "1969-12-31T23:59:59.999GMT",
          "sparkUser": "test",
          "completed": False
        }, {
          "attemptId": "1",
          "startTime": "2017-12-24T03:12:50.763GMT",
          "endTime": "2017-12-24T03:19:22.178GMT",
          "sparkUser": "test",
          "completed": True
      }]
    }]

  def applications(self):
    return self.APPS

  def executors(self, job):
    EXECUTORS_LISTS = {
      u'application_1513618343677_0018/1': [{
        u'diskUsed': 0,
        u'totalShuffleWrite': 0,
        u'totalCores': 0,
        u'executorLogs': {
          u'stderr': u'http://localhost:8042/node/containerlogs/container_1513618343677_0018_01_000001/test/stderr?start=-4096',
          u'stdout': u'http://localhost:8042/node/containerlogs/container_1513618343677_0018_01_000001/test/stdout?start=-4096'
        },
        u'totalInputBytes': 0,
        u'rddBlocks': 0,
        u'maxMemory': 515553361,
        u'totalShuffleRead': 0,
        u'totalTasks': 0,
        u'activeTasks': 0,
        u'failedTasks': 0,
        u'completedTasks': 0,
        u'hostPort': u'172.31.122.54:43234',
        u'maxTasks': 0, u'totalGCTime': 0,
        u'isBlacklisted': False,
        u'memoryUsed': 0,
        u'id': u'driver',
        u'isActive': True,
        u'totalDuration': 0
      }],
      u'application_1513618343677_0020/2' : [{
        u'diskUsed': 0,
        u'totalShuffleWrite': 0,
        u'totalCores': 0,
        u'executorLogs': {
          u'stderr': u'http://localhost:8042/node/containerlogs/container_1513618343677_0020_01_000001/test/stderr?start=-4096',
          u'stdout': u'http://localhost:8042/node/containerlogs/container_1513618343677_0020_01_000001/test/stdout?start=-4096'},
        u'totalInputBytes': 0,
        u'rddBlocks': 0,
        u'maxMemory': 515553361,
        u'totalShuffleRead': 0,
        u'totalTasks': 0,
        u'activeTasks': 0,
        u'failedTasks': 0,
        u'completedTasks': 0,
        u'hostPort': u'172.31.122.65:38210',
        u'maxTasks': 0,
        u'totalGCTime': 0,
        u'isBlacklisted': False,
        u'memoryUsed': 0,
        u'id': u'driver',
        u'isActive': True,
        u'totalDuration': 0}]
    }
    app_id = self.get_real_app_id(job)
    if not app_id:
      return []

    return EXECUTORS_LISTS[app_id] if app_id in EXECUTORS_LISTS else []

  def download_executors_logs(self, request, job, name, offset):
    return 'dummy_logs'

  def download_executor_logs(self, user, executor, name, offset):
    return 'dummy_log'

  def get_executors_loglinks(self, job):
    return None

class HistoryServerApi(MockMapreduce2Api):

  def __init__(self, hs_url=None): pass

  def job(self, user, job_id):
    if '1356251510842_0054' == job_id:
      return {
          u'job': {
              u'reducesCompleted': 1, u'avgMapTime': 1798, u'avgMergeTime': 1479, u'id': job_id,
              u'successfulReduceAttempts': 1, u'successfulMapAttempts': 2, u'uberized': False, u'reducesTotal': 1,
              u'state': u'KILLED', u'failedReduceAttempts': 0, u'mapsCompleted': 2,
              u'killedMapAttempts': 0, u'diagnostics': u'', u'mapsTotal': 2, u'user': u'test',
              u'startTime': 1357151916268, u'avgReduceTime': 137,
              u'finishTime': 1357151923925, u'name': u'oozie:action:T=map-reduce:W=MapReduce-copy:A=Sleep:ID=0000004-121223003201296-oozie-oozi-W',
              u'avgShuffleTime': 1421, u'queue': u'default', u'killedReduceAttempts': 0, u'failedMapAttempts': 0
          }
      }
    else:
      return {
          u'job': {
              u'reducesCompleted': 1, u'avgMapTime': 1798, u'avgMergeTime': 1479, u'id': u'job_1356251510842_0009',
              u'successfulReduceAttempts': 1, u'successfulMapAttempts': 2, u'uberized': False, u'reducesTotal': 1,
              u'state': u'SUCCEEDED', u'failedReduceAttempts': 0, u'mapsCompleted': 2,
              u'killedMapAttempts': 0, u'diagnostics': u'', u'mapsTotal': 2, u'user': u'test',
              u'startTime': 0, u'avgReduceTime': 137,
              u'finishTime': 1357151923925, u'name': u'oozie:action:T=map-reduce:W=MapReduce-copy:A=Sleep:ID=0000004-121223003201296-oozie-oozi-W',
              u'avgShuffleTime': 1421, u'queue': u'default', u'killedReduceAttempts': 0, u'failedMapAttempts': 0
          }
      }


def test_make_log_links():
  """
   Unit test for models.LinkJobLogs._make_links
  """

  # FileBrowser
  assert_equal(
      """<a href="/filebrowser/view=/user/romain/tmp">hdfs://localhost:8020/user/romain/tmp</a>  &lt;dir&gt;""",
      LinkJobLogs._make_links('hdfs://localhost:8020/user/romain/tmp  <dir>')
  )
  assert_equal(
      """<a href="/filebrowser/view=/user/romain/tmp">hdfs://localhost:8020/user/romain/tmp</a>&lt;dir&gt;""",
      LinkJobLogs._make_links('hdfs://localhost:8020/user/romain/tmp<dir>')
  )
  assert_equal(
      """output: <a href="/filebrowser/view=/user/romain/tmp">/user/romain/tmp</a>  &lt;dir&gt;""",
      LinkJobLogs._make_links('output: /user/romain/tmp  <dir>')
  )
  assert_equal(
      'Successfully read 3760 records (112648 bytes) from: &quot;<a href="/filebrowser/view=/user/hue/pig/examples/data/midsummer.txt">/user/hue/pig/examples/data/midsummer.txt</a>&quot;',
      LinkJobLogs._make_links('Successfully read 3760 records (112648 bytes) from: "/user/hue/pig/examples/data/midsummer.txt"')
  )
  assert_equal(
      'data,upper_case  MAP_ONLY  <a href="/filebrowser/view=/user/romain/out/fffff">hdfs://localhost:8020/user/romain/out/fffff</a>,',
      LinkJobLogs._make_links('data,upper_case  MAP_ONLY  hdfs://localhost:8020/user/romain/out/fffff,')
  )
  assert_equal(
      'MAP_ONLY  <a href="/filebrowser/view=/user/romain/out/fffff">hdfs://localhost:8020/user/romain/out/fffff</a>\n2013',
      LinkJobLogs._make_links('MAP_ONLY  hdfs://localhost:8020/user/romain/out/fffff\n2013')
  )
  assert_equal(
      ' <a href="/filebrowser/view=/jobs.tsv">/jobs.tsv</a> ',
      LinkJobLogs._make_links(' /jobs.tsv ')
  )
  assert_equal(
      '<a href="/filebrowser/view=/user/romain/job_pos_2012.tsv">hdfs://localhost:8020/user/romain/job_pos_2012.tsv</a>',
      LinkJobLogs._make_links('hdfs://localhost:8020/user/romain/job_pos_2012.tsv')
  )

  # JobBrowser
  assert_equal(
      """<a href="/hue/jobbrowser/jobs/job_201306261521_0058">job_201306261521_0058</a>""",
      LinkJobLogs._make_links('job_201306261521_0058')
  )
  assert_equal(
      """Hadoop Job IDs executed by Pig: <a href="/hue/jobbrowser/jobs/job_201306261521_0058">job_201306261521_0058</a>""",
      LinkJobLogs._make_links('Hadoop Job IDs executed by Pig: job_201306261521_0058')
  )
  assert_equal(
      """MapReduceLauncher  - HadoopJobId: <a href="/hue/jobbrowser/jobs/job_201306261521_0058">job_201306261521_0058</a>""",
      LinkJobLogs._make_links('MapReduceLauncher  - HadoopJobId: job_201306261521_0058')
  )
  assert_equal(
      """- More information at: http://localhost:50030/jobdetails.jsp?jobid=<a href="/hue/jobbrowser/jobs/job_201306261521_0058">job_201306261521_0058</a>""",
      LinkJobLogs._make_links('- More information at: http://localhost:50030/jobdetails.jsp?jobid=job_201306261521_0058')
  )
  assert_equal(
      """ Logging error messages to: <a href="/hue/jobbrowser/jobs/job_201307091553_0028">job_201307091553_0028</a>/attempt_201307091553_002""",
      LinkJobLogs._make_links(' Logging error messages to: job_201307091553_0028/attempt_201307091553_002')
  )
  assert_equal(
      """ pig-<a href="/hue/jobbrowser/jobs/job_201307091553_0028">job_201307091553_0028</a>.log""",
      LinkJobLogs._make_links(' pig-job_201307091553_0028.log')
  )
  assert_equal(
      """MapReduceLauncher  - HadoopJobId: <a href="/hue/jobbrowser/jobs/job_201306261521_0058">job_201306261521_0058</a>. Look at the UI""",
      LinkJobLogs._make_links('MapReduceLauncher  - HadoopJobId: job_201306261521_0058. Look at the UI')
  )
