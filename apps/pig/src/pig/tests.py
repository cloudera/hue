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
import time

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from nose.tools import assert_true, assert_equal

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access
from hadoop import pseudo_hdfs4
from liboozie.oozie_api_test import OozieServerProvider
from oozie.tests import OozieBase

from pig.models import create_or_update_script, PigScript
from pig.api import OozieApi


class TestPigBase(object):
  SCRIPT_ATTRS = {
      'id': 1000,
      'name': 'Test',
      'script': 'A = LOAD "$data"; STORE A INTO "$output";',
      'parameters': [],
      'resources': [],
      'hadoopProperties': []
  }

  def setUp(self):
    self.c = make_logged_in_client(is_superuser=False)
    grant_access("test", "test", "pig")
    self.user = User.objects.get(username='test')

  def create_script(self):
    return create_script(self.user)


def create_script(user, xattrs=None):
  attrs = {'user': user}
  attrs.update(TestPigBase.SCRIPT_ATTRS)
  if xattrs is not None:
    attrs.update(xattrs)
  return create_or_update_script(**attrs)

  def make_log_links(self):
    # FileBrowser
    assert_equal(
        """<a href="/filebrowser/view/user/romain/tmp" target="_blank">hdfs://localhost:8020/user/romain/tmp</a>  &lt;dir&gt;""",
        OozieApi._make_links('hdfs://localhost:8020/user/romain/tmp  <dir>')
    )
    assert_equal(
        """<a href="/filebrowser/view/user/romain/tmp" target="_blank">hdfs://localhost:8020/user/romain/tmp</a>&lt;dir&gt;""",
        OozieApi._make_links('hdfs://localhost:8020/user/romain/tmp<dir>')
    )
    assert_equal(
        """output: <a href="/filebrowser/view/user/romain/tmp" target="_blank">/user/romain/tmp</a>  &lt;dir&gt;""",
        OozieApi._make_links('output: /user/romain/tmp  <dir>')
    )
    assert_equal(
        'Successfully read 3760 records (112648 bytes) from: &quot;<a href="/filebrowser/view/user/hue/pig/examples/data/midsummer.txt" target="_blank">/user/hue/pig/examples/data/midsummer.txt</a>&quot;',
        OozieApi._make_links('Successfully read 3760 records (112648 bytes) from: "/user/hue/pig/examples/data/midsummer.txt"')
    )
    assert_equal(
        'data,upper_case  MAP_ONLY  <a href="/filebrowser/view/user/romain/out/fffff" target="_blank">hdfs://localhost:8020/user/romain/out/fffff</a>,',
        OozieApi._make_links('data,upper_case  MAP_ONLY  hdfs://localhost:8020/user/romain/out/fffff,')
    )
    assert_equal(
        'MAP_ONLY  <a href="/filebrowser/view/user/romain/out/fffff" target="_blank">hdfs://localhost:8020/user/romain/out/fffff</a>\n2013',
        OozieApi._make_links('MAP_ONLY  hdfs://localhost:8020/user/romain/out/fffff\n2013')
    )

    # JobBrowser
    assert_equal(
        """<a href="/jobbrowser/jobs/job_201306261521_0058" target="_blank">job_201306261521_0058</a>""",
        OozieApi._make_links('job_201306261521_0058')
    )
    assert_equal(
        """Hadoop Job IDs executed by Pig: <a href="/jobbrowser/jobs/job_201306261521_0058" target="_blank">job_201306261521_0058</a>""",
        OozieApi._make_links('Hadoop Job IDs executed by Pig: job_201306261521_0058')
    )
    assert_equal(
        """MapReduceLauncher  - HadoopJobId: <a href="/jobbrowser/jobs/job_201306261521_0058" target="_blank">job_201306261521_0058</a>""",
        OozieApi._make_links('MapReduceLauncher  - HadoopJobId: job_201306261521_0058')
    )
    assert_equal(
        """- More information at: http://localhost:50030/jobdetails.jsp?jobid=<a href="/jobbrowser/jobs/job_201306261521_0058" target="_blank">job_201306261521_0058</a>""",
        OozieApi._make_links('- More information at: http://localhost:50030/jobdetails.jsp?jobid=job_201306261521_0058')
    )


class TestMock(TestPigBase):

  def test_create_script(self):
    pig_script = self.create_script()
    assert_equal('Test', pig_script.dict['name'])

  def test_save(self):
    attrs = {'user': self.user,}
    attrs.update(TestPigBase.SCRIPT_ATTRS)
    attrs['parameters'] = json.dumps(TestPigBase.SCRIPT_ATTRS['parameters'])
    attrs['resources'] = json.dumps(TestPigBase.SCRIPT_ATTRS['resources'])
    attrs['hadoopProperties'] = json.dumps(TestPigBase.SCRIPT_ATTRS['hadoopProperties'])

    # Save
    self.c.post(reverse('pig:save'), data=attrs, follow=True)

    # Update
    self.c.post(reverse('pig:save'), data=attrs, follow=True)


class TestWithHadoop(OozieBase):

  def setUp(self):
    super(TestWithHadoop, self).setUp()
    self.c = make_logged_in_client(is_superuser=False)
    grant_access("test", "test", "pig")
    self.user = User.objects.get(username='test')
    self.c.post(reverse('pig:install_examples'))

  def test_create_workflow(self):
    cluster = pseudo_hdfs4.shared_cluster()
    api = OozieApi(cluster.fs, self.user)

    xattrs = {
      'parameters': [
        {'name': 'output', 'value': '/tmp'},
        {'name': '-param', 'value': 'input=/data'}, # Alternative way for params
        {'name': '-optimizer_off', 'value': 'SplitFilter'},
        {'name': '-v', 'value': ''},
       ],
      'resources': [
        {'type': 'file', 'value': '/tmp/file'},
        {'type': 'archive', 'value': '/tmp/file.zip'},
      ],
      'hadoopProperties': [
        {'name': 'mapred.map.tasks.speculative.execution', 'value': 'false'},
        {'name': 'mapred.job.queue', 'value': 'fast'},
      ]
    }

    pig_script = create_script(self.user, xattrs)
    params = json.dumps([
      {'name': 'output', 'value': '/tmp2'},
    ])

    workflow = api._create_workflow(pig_script, params)
    pig_action = workflow.start.get_child('to').get_full_node()

    assert_equal([
        {u'type': u'argument', u'value': u'-param'}, {u'type': u'argument', u'value': u'output=/tmp2'},
        {u'type': u'argument', u'value': u'-param'}, {u'type': u'argument', u'value': u'input=/data'},
        {u'type': u'argument', u'value': u'-optimizer_off'}, {u'type': u'argument', u'value': u'SplitFilter'},
        {u'type': u'argument', u'value': u'-v'},
    ], pig_action.get_params())

    assert_equal([
        {u'name': u'mapred.map.tasks.speculative.execution', u'value': u'false'},
        {u'name': u'mapred.job.queue', u'value': u'fast'},
    ], pig_action.get_properties())

    assert_equal(['/tmp/file'], pig_action.get_files())

    assert_equal([
        {u'dummy': u'', u'name': u'/tmp/file.zip'},
    ], pig_action.get_archives())

  def wait_until_completion(self, pig_script_id, timeout=300.0, step=5, expected_status='SUCCEEDED'):
    script = PigScript.objects.get(id=pig_script_id)
    job_id = script.dict['job_id']

    response = self.c.get(reverse('pig:watch', args=[job_id]))
    response = json.loads(response.content)

    start = time.time()

    while response['workflow']['status'] in ['PREP', 'RUNNING'] and time.time() - start < timeout:
      time.sleep(step)
      response = self.c.get(reverse('pig:watch', args=[job_id]))
      response = json.loads(response.content)

    logs = OozieServerProvider.oozie.get_job_log(job_id)

    if response['workflow']['status'] != expected_status:
      msg = "[%d] %s took more than %d to complete or %s: %s" % (time.time(), job_id, timeout, response['workflow']['status'], logs)
      raise Exception(msg)

    return pig_script_id

  def test_submit(self):
    script = PigScript.objects.get(id=1)
    script_dict = script.dict

    post_data = {
      'id': script.id,
      'name': script_dict['name'],
      'script': script_dict['script'],
      'user': script.owner,
      'parameters': json.dumps(script_dict['parameters']),
      'resources': json.dumps(script_dict['resources']),
      'hadoopProperties': json.dumps(script_dict['hadoopProperties']),
      'submissionVariables': json.dumps([{"name": "output", "value": '/tmp/test_pig'}]),
    }

    response = self.c.post(reverse('pig:run'), data=post_data, follow=True)
    job_id = json.loads(response.content)['id']

    self.wait_until_completion(job_id)

  def test_stop(self):
    script = PigScript.objects.get(id=1)
    script_dict = script.dict

    post_data = {
      'id': script.id,
      'name': script_dict['name'],
      'script': script_dict['script'],
      'user': script.owner,
      'parameters': json.dumps(script_dict['parameters']),
      'resources': json.dumps(script_dict['resources']),
      'hadoopProperties': json.dumps(script_dict['hadoopProperties']),
      'submissionVariables': json.dumps([{"name": "output", "value": '/tmp/test_pig'}]),
    }

    submit_response = self.c.post(reverse('pig:run'), data=post_data, follow=True)
    script = PigScript.objects.get(id=json.loads(submit_response.content)['id'])
    assert_true(script.dict['job_id'], script.dict)

    self.c.post(reverse('pig:stop'), data={'id': script.id}, follow=True)
    self.wait_until_completion(json.loads(submit_response.content)['id'], expected_status='KILLED')
