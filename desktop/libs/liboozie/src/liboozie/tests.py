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

from nose.tools import assert_equal
from oozie.tests import MockOozieApi

from desktop.lib.test_utils import reformat_xml

from hadoop import cluster
from hadoop.conf import HDFS_CLUSTERS, MR_CLUSTERS, YARN_CLUSTERS
from liboozie.types import WorkflowAction, Coordinator
from liboozie.submittion import Submission
from liboozie.utils import config_gen


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


class MockFs(object):
  def __init__(self, logical_name=None):

    self.fs_defaultfs = 'hdfs://curacao:8020'
    if logical_name:
      self.logical_name = logical_name
    else:
      self.logical_name = ''


def test_update_properties():
  finish = []
  finish.append(MR_CLUSTERS['default'].SUBMIT_TO.set_for_testing(True))
  finish.append(YARN_CLUSTERS['default'].SUBMIT_TO.set_for_testing(True))
  try:
    properties = {
        'user.name': 'hue',
        'test.1': 'http://localhost/test?test1=test&test2=test',
        'nameNode': 'hdfs://curacao:8020',
        'jobTracker': 'jtaddress'
    }

    final_properties = properties.copy()
    submission = Submission(None, properties=properties, oozie_id='test', fs=MockFs())
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
