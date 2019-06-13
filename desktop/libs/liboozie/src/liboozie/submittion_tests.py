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
from nose.plugins.attrib import attr
from nose.tools import assert_equal, assert_true, assert_not_equal

from hadoop import cluster, pseudo_hdfs4
from hadoop.conf import HDFS_CLUSTERS, MR_CLUSTERS, YARN_CLUSTERS

from desktop.lib.test_utils import clear_sys_caches
from desktop.lib.django_test_util import make_logged_in_client
from oozie.tests import OozieMockBase
from useradmin.views import ensure_home_directory

from liboozie.submittion import Submission


LOG = logging.getLogger(__name__)


@attr('integration')
@attr('requires_hadoop')
def test_copy_files():
  cluster = pseudo_hdfs4.shared_cluster()

  try:
    c = make_logged_in_client()
    user = User.objects.get(username='test')
    ensure_home_directory(cluster.fs, user)

    prefix = '/tmp/test_copy_files'

    if cluster.fs.exists(prefix):
      cluster.fs.rmtree(prefix, skip_trash=True) # admin user might not have a home directory

    # Jars in various locations
    deployment_dir = '%s/workspace' % prefix
    external_deployment_dir = '%s/deployment' % prefix
    jar_1 = '%s/udf1.jar' % prefix
    jar_2 = '%s/lib/udf2.jar' % prefix
    jar_3 = '%s/udf3.jar' % deployment_dir
    jar_4 = '%s/lib/udf4.jar' % deployment_dir # Never move

    cluster.fs.mkdir(prefix)
    cluster.fs.create(jar_1)
    cluster.fs.create(jar_2)
    cluster.fs.create(jar_3)
    cluster.fs.create(jar_4)

    class MockNode():
      def __init__(self, jar_path):
        self.jar_path = jar_path

    class MockJob():
      def __init__(self):
        self.node_list = [
            MockNode(jar_1),
            MockNode(jar_2),
            MockNode(jar_3),
            MockNode(jar_4),
        ]

      def get_application_filename(self):
        return 'workflow.xml'

    submission = Submission(user, job=MockJob(), fs=cluster.fs, jt=cluster.jt)

    submission._copy_files(deployment_dir, "<xml>My XML</xml>")
    submission._copy_files(external_deployment_dir, "<xml>My XML</xml>")

    # All sources still there
    assert_true(cluster.fs.exists(jar_1))
    assert_true(cluster.fs.exists(jar_2))
    assert_true(cluster.fs.exists(jar_3))
    assert_true(cluster.fs.exists(jar_4))

    deployment_dir = deployment_dir + '/lib'
    external_deployment_dir = external_deployment_dir + '/lib'

    list_dir_workspace = cluster.fs.listdir(deployment_dir)
    list_dir_deployement = cluster.fs.listdir(external_deployment_dir)

    # All destinations there
    assert_true(cluster.fs.exists(deployment_dir + '/udf1.jar'), list_dir_workspace)
    assert_true(cluster.fs.exists(deployment_dir + '/udf2.jar'), list_dir_workspace)
    assert_true(cluster.fs.exists(deployment_dir + '/udf3.jar'), list_dir_workspace)
    assert_true(cluster.fs.exists(deployment_dir + '/udf4.jar'), list_dir_workspace)

    assert_true(cluster.fs.exists(external_deployment_dir + '/udf1.jar'), list_dir_deployement)
    assert_true(cluster.fs.exists(external_deployment_dir + '/udf2.jar'), list_dir_deployement)
    assert_true(cluster.fs.exists(external_deployment_dir + '/udf3.jar'), list_dir_deployement)
    assert_true(cluster.fs.exists(external_deployment_dir + '/udf4.jar'), list_dir_deployement)

    stats_udf1 = cluster.fs.stats(deployment_dir + '/udf1.jar')
    stats_udf2 = cluster.fs.stats(deployment_dir + '/udf2.jar')
    stats_udf3 = cluster.fs.stats(deployment_dir + '/udf3.jar')
    stats_udf4 = cluster.fs.stats(deployment_dir + '/udf4.jar')

    submission._copy_files('%s/workspace' % prefix, "<xml>My XML</xml>")

    assert_not_equal(stats_udf1['fileId'], cluster.fs.stats(deployment_dir + '/udf1.jar')['fileId'])
    assert_not_equal(stats_udf2['fileId'], cluster.fs.stats(deployment_dir + '/udf2.jar')['fileId'])
    assert_not_equal(stats_udf3['fileId'], cluster.fs.stats(deployment_dir + '/udf3.jar')['fileId'])
    assert_equal(stats_udf4['fileId'], cluster.fs.stats(deployment_dir + '/udf4.jar')['fileId'])

  finally:
    try:
      cluster.fs.rmtree(prefix, skip_trash=True)
    except:
      LOG.exception('failed to remove %s' % prefix)


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
    finish.append(MR_CLUSTERS.set_for_testing({'default': {}}))
    finish.append(MR_CLUSTERS['default'].SUBMIT_TO.set_for_testing(True))
    finish.append(YARN_CLUSTERS.set_for_testing({'default': {}}))
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

      clear_sys_caches()
      fs = cluster.get_hdfs()
      final_properties = properties.copy()
      final_properties.update({
        'jobTracker': 'jtaddress',
        'nameNode': fs.fs_defaultfs
      })
      submission = Submission(None, properties=properties, oozie_id='test', fs=fs, jt=None)
      assert_equal(properties, submission.properties)
      submission._update_properties('jtaddress', 'deployment-directory')
      assert_equal(final_properties, submission.properties)

      finish.append(HDFS_CLUSTERS['default'].LOGICAL_NAME.set_for_testing('namenode'))
      finish.append(MR_CLUSTERS['default'].LOGICAL_NAME.set_for_testing('jobtracker'))
      clear_sys_caches()
      fs = cluster.get_hdfs()
      final_properties = properties.copy()
      final_properties.update({
        'jobTracker': 'jobtracker',
        'nameNode': 'namenode'
      })
      submission = Submission(None, properties=properties, oozie_id='test', fs=fs, jt=None)
      assert_equal(properties, submission.properties)
    finally:
      clear_sys_caches()
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
