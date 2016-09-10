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

from django.contrib.auth.models import User
from nose.tools import assert_equal

import desktop.conf as desktop_conf
from desktop.lib.test_utils import reformat_xml

from liboozie import conf
from liboozie.types import WorkflowAction, Coordinator
from liboozie.utils import config_gen
from oozie.tests import MockOozieApi


LOG = logging.getLogger(__name__)


def test_valid_external_id():
  action = WorkflowAction(MockOozieApi.JSON_WORKFLOW_LIST[0])
  assert_equal('job_201208072118_0044', action.externalId)
  assert_equal('/jobbrowser/jobs/job_201208072118_0044/single_logs', action.get_absolute_log_url())
  assert_equal('/jobbrowser/jobs/job_201208072118_0044', action.get_external_id_url())

  action = WorkflowAction(MockOozieApi.JSON_WORKFLOW_LIST[1])
  assert_equal('-', action.externalId)
  assert_equal(None, action.get_absolute_log_url())
  assert_equal(None, action.get_external_id_url())

  action = WorkflowAction(MockOozieApi.JSON_WORKFLOW_LIST[2])
  assert_equal('', action.externalId)
  assert_equal(None, action.get_absolute_log_url())
  assert_equal(None, action.get_external_id_url())

  action = WorkflowAction(MockOozieApi.JSON_WORKFLOW_LIST[3])
  assert_equal(None, action.externalId)
  assert_equal(None, action.get_absolute_log_url())
  assert_equal(None, action.get_external_id_url())


def aggregate_coordinator_instances():
  dates = ['1', '2', '3', '6', '7', '8', '10', '12', '15', '16', '20', '23', '30', '40']
  assert_equal(['1-3', '6-8', '10-10', '12-12', '15-16', '20-20', '23-23', '30-30', '40-40'], Coordinator.aggreate(dates))


def test_config_gen():
  properties = {
    'user.name': 'hue',
    'test.1': 'http://localhost/test?test1=test&test2=test'
  }
  assert_equal(reformat_xml("""<configuration>
<property>
  <name>test.1</name>
  <value><![CDATA[http://localhost/test?test1=test&test2=test]]></value>
</property>
<property>
  <name>user.name</name>
  <value><![CDATA[hue]]></value>
</property>
</configuration>"""), reformat_xml(config_gen(properties)))

def test_config_gen_negative():
  properties = {
    'user.name': 'hue<foo>bar</foo>',
    'test.1': 'http://localhost/test?test1=test&test2=test]]>&test3=test'
  }
  assert_equal(reformat_xml("""<configuration>
<property>
  <name>test.1</name>
  <value><![CDATA[http://localhost/test?test1=test&test2=test&test3=test]]></value>
</property>
<property>
  <name>user.name</name>
  <value><![CDATA[hue<foo>bar</foo>]]></value>
</property>
</configuration>"""), reformat_xml(config_gen(properties)))

def test_ssl_validate():
  for desktop_kwargs, conf_kwargs, expected in [
      ({'present': False}, {'present': False}, True),
      ({'present': False}, {'data': False}, False),
      ({'present': False}, {'data': True}, True),

      ({'data': False}, {'present': False}, False),
      ({'data': False}, {'data': False}, False),
      ({'data': False}, {'data': True}, True),

      ({'data': True}, {'present': False}, True),
      ({'data': True}, {'data': False}, False),
      ({'data': True}, {'data': True}, True),
      ]:
    resets = [
      desktop_conf.SSL_VALIDATE.set_for_testing(**desktop_kwargs),
      conf.SSL_CERT_CA_VERIFY.set_for_testing(**conf_kwargs),
    ]

    try:
      assert_equal(conf.SSL_CERT_CA_VERIFY.get(), expected,
          'desktop:%s conf:%s expected:%s got:%s' % (desktop_kwargs, conf_kwargs, expected, conf.SSL_CERT_CA_VERIFY.get()))
    finally:
      for reset in resets:
        reset()
