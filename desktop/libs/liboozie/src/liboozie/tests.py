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

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import reformat_xml

from hadoop import cluster
from hadoop.conf import HDFS_CLUSTERS, MR_CLUSTERS, YARN_CLUSTERS
from liboozie.types import WorkflowAction, Coordinator
from liboozie.submittion import Submission
from liboozie.utils import config_gen
from oozie.tests import MockOozieApi


LOG = logging.getLogger(__name__)


def test_valid_external_id():
  assert_equal('job_201208072118_0044', WorkflowAction(MockOozieApi.JSON_WORKFLOW_LIST[0]).externalId)
  assert_equal(None, WorkflowAction(MockOozieApi.JSON_WORKFLOW_LIST[1]).externalId)
  assert_equal(None, WorkflowAction(MockOozieApi.JSON_WORKFLOW_LIST[2]).externalId)
  assert_equal(None, WorkflowAction(MockOozieApi.JSON_WORKFLOW_LIST[3]).externalId)


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


def test_update_properties():
  finish = []
  finish.append(MR_CLUSTERS['default'].SUBMIT_TO.set_for_testing(True))
  finish.append(YARN_CLUSTERS['default'].SUBMIT_TO.set_for_testing(True))
  try:
    properties = {
      'user.name': 'hue',
      'test.1': 'http://localhost/test?test1=test&test2=test'
    }

    final_properties = properties.copy()
    submission = Submission(None, properties=properties, oozie_id='test')
    assert_equal(properties, submission.properties)
    submission._update_properties('jtaddress', 'deployment-directory')
    assert_equal(final_properties, submission.properties)

    cluster.clear_caches()
    fs = cluster.get_hdfs()
    jt = cluster.get_next_ha_mrcluster()[1]
    final_properties = properties.copy()
    final_properties.update({
      'jobTracker': 'jtaddress',
      'nameNode': fs.fs_defaultfs
    })
    submission = Submission(None, properties=properties, oozie_id='test', fs=fs, jt=jt)
    assert_equal(properties, submission.properties)
    submission._update_properties('jtaddress', 'deployment-directory')
    assert_equal(final_properties, submission.properties)

    finish.append(HDFS_CLUSTERS['default'].LOGICAL_NAME.set_for_testing('namenode'))
    finish.append(MR_CLUSTERS['default'].LOGICAL_NAME.set_for_testing('jobtracker'))
    cluster.clear_caches()
    fs = cluster.get_hdfs()
    jt = cluster.get_next_ha_mrcluster()[1]
    final_properties = properties.copy()
    final_properties.update({
      'jobTracker': 'jobtracker',
      'nameNode': 'namenode'
    })
    submission = Submission(None, properties=properties, oozie_id='test', fs=fs, jt=jt)
    assert_equal(properties, submission.properties)
    submission._update_properties('jtaddress', 'deployment-directory')
    assert_equal(final_properties, submission.properties)
  finally:
    cluster.clear_caches()
    for reset in finish:
      reset()


class TestSubmission():

  def setUp(self):
    self.c = make_logged_in_client(is_superuser=False)
    self.user = User.objects.get(username='test')

  def test_get_external_parameters(self):
    xml = """
<workflow-app name="Pig" xmlns="uri:oozie:workflow:0.4">
    <start to="Pig"/>
    <action name="Pig">
        <pig>
            <job-tracker>${jobTracker}</job-tracker>
            <name-node>${nameNode}</name-node>
            <prepare>
                  <delete path="${output}"/>
            </prepare>
            <script>aggregate.pig</script>
              <argument>-param</argument>
              <argument>INPUT=${input}</argument>
              <argument>-param</argument>
              <argument>OUTPUT=${output}</argument>
        </pig>
        <ok to="end"/>
        <error to="kill"/>
    </action>
    <kill name="kill">
        <message>Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]</message>
    </kill>
    <end name="end"/>
</workflow-app>
    """

    properties = """
#
# Licensed to the Hue
#

nameNode=hdfs://localhost:8020
jobTracker=localhost:8021
queueName=default
examplesRoot=examples

oozie.use.system.libpath=true

oozie.wf.application.path=${nameNode}/user/${user.name}/${examplesRoot}/apps/pig
    """
    parameters = Submission(self.user)._get_external_parameters(xml, properties)

    assert_equal({'oozie.use.system.libpath': 'true',
                   'input': '',
                   'jobTracker': 'localhost:8021',
                   'oozie.wf.application.path': '${nameNode}/user/${user.name}/${examplesRoot}/apps/pig',
                   'examplesRoot': 'examples',
                   'output': '',
                   'nameNode': 'hdfs://localhost:8020',
                   'queueName': 'default'
                  },
                 parameters)
