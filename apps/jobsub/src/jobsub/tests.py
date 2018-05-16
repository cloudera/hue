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
import json
import time

from nose.tools import assert_true, assert_false, assert_equal, assert_raises
from django.contrib.auth.models import User
from django.urls import reverse
from nose.plugins.skip import SkipTest

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access, add_to_group
from desktop.models import Document

from liboozie.oozie_api_tests import OozieServerProvider
from oozie.models import Workflow, Node, Start, Kill, End, Link


LOG = logging.getLogger(__name__)

class TestJobsubWithHadoop(OozieServerProvider):

  def setUp(self):
    OozieServerProvider.setup_class()
    self.cluster.fs.do_as_user('jobsub_test', self.cluster.fs.create_home_dir, '/user/jobsub_test')
    self.cluster.fs.do_as_superuser(self.cluster.fs.chmod, '/user/jobsub_test', 0777, True) # Hum?
    self.client = make_logged_in_client(username='jobsub_test')
    self.user = User.objects.get(username='jobsub_test')

    # Ensure access to MR folder.
    # Need to chmod because jobs are submitted as a
    # different user than what was previously used.
    for i in range(0,10):
      try:
        self.cluster.fs.do_as_superuser(self.cluster.fs.chmod, '/tmp', 0777, recursive=True)
        break
      except Exception, e:
        # chmod failure likely do to async processing of resource deletion.
        # If the directory has improper permissions, should fail later in the test case.
        LOG.warn("Received the following exception while change mode attempt %d of /tmp: %s" % (i, str(e)))
        time.sleep(1)

    self.design = self.create_design()

  def tearDown(self):
    Workflow.objects.all().delete()

  def create_design(self):
    response = self.client.post(reverse('jobsub.views.new_design',
      kwargs={'node_type': 'mapreduce'}),
      data={'name': 'sleep_job',
            'description': '',
            'node_type': 'mapreduce',
            'jar_path': '/user/hue/oozie/workspaces/lib/hadoop-examples.jar',
            'prepares': '[]',
            'files': '[]',
            'archives': '[]',
            'job_properties': '[{\"name\":\"mapred.reduce.tasks\",\"value\":\"1\"},{\"name\":\"mapred.mapper.class\",\"value\":\"org.apache.hadoop.examples.SleepJob\"},{\"name\":\"mapred.reducer.class\",\"value\":\"org.apache.hadoop.examples.SleepJob\"},{\"name\":\"mapred.mapoutput.key.class\",\"value\":\"org.apache.hadoop.io.IntWritable\"},{\"name\":\"mapred.mapoutput.value.class\",\"value\":\"org.apache.hadoop.io.NullWritable\"},{\"name\":\"mapred.output.format.class\",\"value\":\"org.apache.hadoop.mapred.lib.NullOutputFormat\"},{\"name\":\"mapred.input.format.class\",\"value\":\"org.apache.hadoop.examples.SleepJob$SleepInputFormat\"},{\"name\":\"mapred.partitioner.class\",\"value\":\"org.apache.hadoop.examples.SleepJob\"},{\"name\":\"mapred.speculative.execution\",\"value\":\"false\"},{\"name\":\"sleep.job.map.sleep.time\",\"value\":\"0\"},{\"name\":\"sleep.job.reduce.sleep.time\",\"value\":\"${REDUCER_SLEEP_TIME}\"}]'},
      HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert_equal(response.status_code, 200)
    return Workflow.objects.all()[0]

  def test_new_design(self):
    # Ensure the following:
    #   - creator is owner.
    #   - workflow name and description are the same as action name and description.
    #   - workflow has one action.
    assert_false(self.design.managed)
    assert_equal(4, Node.objects.filter(workflow=self.design).count())
    assert_equal(1, Kill.objects.filter(workflow=self.design).count())
    assert_equal(1, Start.objects.filter(workflow=self.design).count())
    assert_equal(1, End.objects.filter(workflow=self.design).count())
    assert_equal(4, Node.objects.filter(workflow=self.design).count())
    assert_equal(3, Link.objects.filter(parent__workflow=self.design).count())

  def test_save_design(self):
    response = self.client.post(reverse('jobsub.views.save_design',
      kwargs={'design_id': self.design.id}),
      data={'name': 'mapreduce1',
            'description': '',
            'node_type': 'mapreduce',
            'jar_path': '/user/hue/oozie/workspaces/lib/hadoop-examples.jar',
            'prepares': '[]',
            'files': '[{"name": "test", "dummy": ""}]',
            'archives': '[]',
            'job_properties': '[{\"name\":\"mapred.reduce.tasks\",\"value\":\"1\"},{\"name\":\"mapred.mapper.class\",\"value\":\"org.apache.hadoop.examples.SleepJob\"},{\"name\":\"mapred.reducer.class\",\"value\":\"org.apache.hadoop.examples.SleepJob\"},{\"name\":\"mapred.mapoutput.key.class\",\"value\":\"org.apache.hadoop.io.IntWritable\"},{\"name\":\"mapred.mapoutput.value.class\",\"value\":\"org.apache.hadoop.io.NullWritable\"},{\"name\":\"mapred.output.format.class\",\"value\":\"org.apache.hadoop.mapred.lib.NullOutputFormat\"},{\"name\":\"mapred.input.format.class\",\"value\":\"org.apache.hadoop.examples.SleepJob$SleepInputFormat\"},{\"name\":\"mapred.partitioner.class\",\"value\":\"org.apache.hadoop.examples.SleepJob\"},{\"name\":\"mapred.speculative.execution\",\"value\":\"false\"},{\"name\":\"sleep.job.map.sleep.time\",\"value\":\"0\"},{\"name\":\"sleep.job.reduce.sleep.time\",\"value\":\"${REDUCER_SLEEP_TIME}\"}]'},
      HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert_equal(response.status_code, 200)
    self.design = Workflow.objects.get(id=self.design.id)
    assert_equal(self.design.start.get_child('to').get_full_node().files, '[{"dummy": "", "name": "test"}]')

  def test_get_design(self):
    response = self.client.get(reverse('jobsub.views.get_design',
      kwargs={'design_id': self.design.id}),
      HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert_equal(response.status_code, 200)

    client_note_me = make_logged_in_client(username='jobsub_test_note_me', is_superuser=False)
    grant_access("jobsub_test_note_me", "jobsub_test_note_me", "jobsub")
    add_to_group("jobsub_test_note_me")

    response = client_note_me.get(reverse('jobsub.views.get_design',
      kwargs={'design_id': self.design.id}),
      HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert_equal(response.status_code, 500)
    data = json.loads(response.content)
    assert_true('does not have the permissions required to access document' in data.get('message', ''), response.content)

  def test_delete_design(self):
    # Trash
    n_available = Document.objects.available_docs(Workflow, self.user).count()
    n_trashed = Document.objects.trashed_docs(Workflow, self.user).count()

    response = self.client.post(reverse('jobsub.views.delete_design',
      kwargs={'design_id': self.design.id}),
      follow=True,
      HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    assert_equal(response.status_code, 200)
    assert_equal(n_available - 1, Document.objects.available_docs(Workflow, self.user).count())
    assert_equal(n_trashed + 1, Document.objects.trashed_docs(Workflow, self.user).count())

    # Destroy
    response = self.client.post(reverse('jobsub.views.delete_design',
      kwargs={'design_id': self.design.id}) + '?skip_trash',
      follow=True,
      HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    assert_equal(response.status_code, 200)
    assert_equal(n_available - 1, Document.objects.available_docs(Workflow, self.user).count())
    assert_equal(n_trashed, Document.objects.trashed_docs(Workflow, self.user).count())

  def test_clone_design(self):
    #@TODO@ Prakash fix this test
    raise SkipTest
    n_available = Document.objects.available_docs(Workflow, self.user).count()

    response = self.client.post(reverse('jobsub.views.clone_design',
      kwargs={'design_id': self.design.id}),
      follow=True,
      HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    assert_equal(response.status_code, 200)
    assert_equal(n_available + 1, Document.objects.available_docs(Workflow, self.user).count())

  def test_restore_design(self):
    n_available = Document.objects.available_docs(Workflow, self.user).count()
    n_trashed = Document.objects.trashed_docs(Workflow, self.user).count()

    response = self.client.post(reverse('jobsub.views.delete_design',
      kwargs={'design_id': self.design.id}),
      follow=True,
      HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    assert_equal(response.status_code, 200)
    assert_equal(n_available - 1, Document.objects.available_docs(Workflow, self.user).count())
    assert_equal(n_trashed + 1, Document.objects.trashed_docs(Workflow, self.user).count())

    response = self.client.post(reverse('jobsub.views.restore_design',
      kwargs={'design_id': self.design.id}),
      follow=True,
      HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    assert_equal(response.status_code, 200)
    assert_equal(n_available, Document.objects.available_docs(Workflow, self.user).count())
    assert_equal(n_trashed, Document.objects.trashed_docs(Workflow, self.user).count())
