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
from liboozie.oozie_api_test import OozieServerProvider

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
from pig.models import create_or_update_script, PigScript
from oozie.tests import OozieBase


class TestPigBase(object):
  def setUp(self):
    self.c = make_logged_in_client(is_superuser=False)
    grant_access("test", "test", "pig")
    self.user = User.objects.get(username='test')

  def create_script(self):
    attrs = {
      'id': 1000,
      'name': 'Test',
      'script': 'A = LOAD "$data"; STORE A INTO "$output";',
      'user': self.user,
      'parameters': [],
      'resources': [],
    }
    return create_or_update_script(**attrs)


class TestMock(TestPigBase):

  def test_create_script(self):
    pig_script = self.create_script()
    assert_equal('Test', pig_script.dict['name'])


class TestWithHadoop(OozieBase):

  def setUp(self):
    super(TestWithHadoop, self).setUp()
    grant_access("test", "test", "pig")
    self.c.post(reverse('pig:install_examples'))

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
      'submissionVariables': json.dumps([{"name": "output", "value": '/tmp/test_pig'}]),
    }

    response = self.c.post(reverse('pig:run'), data=post_data, follow=True)
    self.wait_until_completion(json.loads(response.content)['id'])

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
      'submissionVariables': json.dumps([{"name": "output", "value": '/tmp/test_pig'}]),
    }

    submit_response = self.c.post(reverse('pig:run'), data=post_data, follow=True)
    script = PigScript.objects.get(id=json.loads(submit_response.content)['id'])
    assert_true(script.dict['job_id'], script.dict)

    stop_response = self.c.post(reverse('pig:stop'), data={'id': script.id}, follow=True)
    self.wait_until_completion(json.loads(submit_response.content)['id'], expected_status='KILLED')
