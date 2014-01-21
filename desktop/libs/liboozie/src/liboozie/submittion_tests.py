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

from nose.tools import assert_equal, assert_true

from hadoop import cluster
from hadoop.conf import HDFS_CLUSTERS, MR_CLUSTERS, YARN_CLUSTERS

from liboozie.submittion import Submission
from oozie.tests import OozieMockBase


LOG = logging.getLogger(__name__)


class MockFs():
  def __init__(self, logical_name=None):

    self.fs_defaultfs = 'hdfs://curacao:8020'
    self.logical_name = logical_name if logical_name else ''


class MockJt():
  def __init__(self, logical_name=None):

    self.logical_name = logical_name if logical_name else ''


class TestSubmission(OozieMockBase):

  def test_get_properties(self):
    submission = Submission(self.user, fs=MockFs())

    assert_equal({}, submission.properties)

    submission._update_properties('curacao:8032', '/deployment_dir')

    assert_equal({
        'jobTracker': 'curacao:8032',
        'nameNode': 'hdfs://curacao:8020'
      }, submission.properties)


  def test_get_logical_properties(self):
    submission = Submission(self.user, fs=MockFs(logical_name='fsname'), jt=MockJt(logical_name='jtname'))

    assert_equal({}, submission.properties)

    submission._update_properties('curacao:8032', '/deployment_dir')

    assert_equal({
        'jobTracker': 'jtname',
        'nameNode': 'fsname'
      }, submission.properties)

  def test_update_properties(self):
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
            <configuration>
              <property>
                <name>mapred.input.format.class</name>
                <value>org.apache.hadoop.examples.SleepJob$SleepInputFormat</value>
              </property>
            </configuration>
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
