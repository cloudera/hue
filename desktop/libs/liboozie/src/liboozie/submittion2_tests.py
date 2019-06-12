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
from nose.tools import assert_equal, assert_true, assert_not_equal, assert_raises

import beeswax

from hadoop import cluster, pseudo_hdfs4
from hadoop.conf import HDFS_CLUSTERS, MR_CLUSTERS, YARN_CLUSTERS

from desktop.lib.test_utils import clear_sys_caches
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.exceptions_renderable import PopupException
from useradmin.views import ensure_home_directory
from oozie.models2 import Node
from oozie.tests import OozieMockBase

from liboozie.conf import USE_LIBPATH_FOR_JARS
from liboozie.credentials import Credentials
from liboozie.credentials_tests import TestCredentials
from liboozie.submission2 import Submission


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
      cluster.fs.rmtree(prefix)

    # Jars in various locations
    deployment_dir = '%s/workspace' % prefix
    external_deployment_dir = '%s/deployment' % prefix
    jar_1 = '%s/udf1.jar' % prefix
    jar_2 = '%s/lib/udf2.jar' % prefix
    jar_3 = '%s/udf3.jar' % deployment_dir
    jar_4 = '%s/lib/udf4.jar' % deployment_dir # Doesn't move
    jar_5 = 'udf5.jar'
    jar_6 = 'lib/udf6.jar' # Doesn't move

    cluster.fs.mkdir(prefix)
    cluster.fs.create(jar_1)
    cluster.fs.create(jar_2)
    cluster.fs.create(jar_3)
    cluster.fs.create(jar_4)
    cluster.fs.create(deployment_dir + '/' + jar_5)
    cluster.fs.create(deployment_dir + '/' + jar_6)

    class MockJob():
      XML_FILE_NAME = 'workflow.xml'

      def __init__(self):
        self.deployment_dir = deployment_dir
        self.nodes = [
            Node({'id': '1', 'type': 'mapreduce', 'properties': {'jar_path': jar_1}}),
            Node({'id': '2', 'type': 'mapreduce', 'properties': {'jar_path': jar_2}}),
            Node({'id': '3', 'type': 'java', 'properties': {'jar_path': jar_3}}),
            Node({'id': '4', 'type': 'java', 'properties': {'jar_path': jar_4}}),

            # Workspace relative paths
            Node({'id': '5', 'type': 'java', 'properties': {'jar_path': jar_5}}),
            Node({'id': '6', 'type': 'java', 'properties': {'jar_path': jar_6}})
        ]

    submission = Submission(user, job=MockJob(), fs=cluster.fs, jt=cluster.jt)

    submission._copy_files(deployment_dir, "<xml>My XML</xml>", {'prop1': 'val1'})
    submission._copy_files(external_deployment_dir, "<xml>My XML</xml>", {'prop1': 'val1'})

    assert_true(cluster.fs.exists(deployment_dir + '/workflow.xml'), deployment_dir)
    assert_true(cluster.fs.exists(deployment_dir + '/job.properties'), deployment_dir)

    # All sources still there
    assert_true(cluster.fs.exists(jar_1))
    assert_true(cluster.fs.exists(jar_2))
    assert_true(cluster.fs.exists(jar_3))
    assert_true(cluster.fs.exists(jar_4))
    assert_true(cluster.fs.exists(deployment_dir + '/' + jar_5))
    assert_true(cluster.fs.exists(deployment_dir + '/' + jar_6))

    # Lib
    deployment_dir = deployment_dir + '/lib'
    external_deployment_dir = external_deployment_dir + '/lib'

    if USE_LIBPATH_FOR_JARS.get():
      assert_true(jar_1 in submission.properties['oozie.libpath'])
      assert_true(jar_2 in submission.properties['oozie.libpath'])
      assert_true(jar_3 in submission.properties['oozie.libpath'])
      assert_true(jar_4 in submission.properties['oozie.libpath'])
      print deployment_dir + '/' + jar_5
      assert_true((deployment_dir + '/' + jar_5) in submission.properties['oozie.libpath'], submission.properties['oozie.libpath'])
      assert_true((deployment_dir + '/' + jar_6) in submission.properties['oozie.libpath'], submission.properties['oozie.libpath'])
    else:
      list_dir_workspace = cluster.fs.listdir(deployment_dir)
      list_dir_deployement = cluster.fs.listdir(external_deployment_dir)

      # All destinations there
      assert_true(cluster.fs.exists(deployment_dir + '/udf1.jar'), list_dir_workspace)
      assert_true(cluster.fs.exists(deployment_dir + '/udf2.jar'), list_dir_workspace)
      assert_true(cluster.fs.exists(deployment_dir + '/udf3.jar'), list_dir_workspace)
      assert_true(cluster.fs.exists(deployment_dir + '/udf4.jar'), list_dir_workspace)
      assert_true(cluster.fs.exists(deployment_dir + '/udf5.jar'), list_dir_workspace)
      assert_true(cluster.fs.exists(deployment_dir + '/udf6.jar'), list_dir_workspace)

      assert_true(cluster.fs.exists(external_deployment_dir + '/udf1.jar'), list_dir_deployement)
      assert_true(cluster.fs.exists(external_deployment_dir + '/udf2.jar'), list_dir_deployement)
      assert_true(cluster.fs.exists(external_deployment_dir + '/udf3.jar'), list_dir_deployement)
      assert_true(cluster.fs.exists(external_deployment_dir + '/udf4.jar'), list_dir_deployement)
      assert_true(cluster.fs.exists(external_deployment_dir + '/udf5.jar'), list_dir_deployement)
      assert_true(cluster.fs.exists(external_deployment_dir + '/udf6.jar'), list_dir_deployement)

      stats_udf1 = cluster.fs.stats(deployment_dir + '/udf1.jar')
      stats_udf2 = cluster.fs.stats(deployment_dir + '/udf2.jar')
      stats_udf3 = cluster.fs.stats(deployment_dir + '/udf3.jar')
      stats_udf4 = cluster.fs.stats(deployment_dir + '/udf4.jar')
      stats_udf5 = cluster.fs.stats(deployment_dir + '/udf5.jar')
      stats_udf6 = cluster.fs.stats(deployment_dir + '/udf6.jar')

      submission._copy_files('%s/workspace' % prefix, "<xml>My XML</xml>", {'prop1': 'val1'})

      assert_not_equal(stats_udf1['fileId'], cluster.fs.stats(deployment_dir + '/udf1.jar')['fileId'])
      assert_not_equal(stats_udf2['fileId'], cluster.fs.stats(deployment_dir + '/udf2.jar')['fileId'])
      assert_not_equal(stats_udf3['fileId'], cluster.fs.stats(deployment_dir + '/udf3.jar')['fileId'])
      assert_equal(stats_udf4['fileId'], cluster.fs.stats(deployment_dir + '/udf4.jar')['fileId'])
      assert_not_equal(stats_udf5['fileId'], cluster.fs.stats(deployment_dir + '/udf5.jar')['fileId'])
      assert_equal(stats_udf6['fileId'], cluster.fs.stats(deployment_dir + '/udf6.jar')['fileId'])

    # Test _create_file()
    submission._create_file(deployment_dir, 'test.txt', data='Test data')
    assert_true(cluster.fs.exists(deployment_dir + '/test.txt'), list_dir_workspace)

  finally:
    try:
      cluster.fs.rmtree(prefix)
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

    assert_equal({'security_enabled': False}, submission.properties)

    submission._update_properties('curacao:8032', '/deployment_dir')

    assert_equal({
        'jobTracker': 'curacao:8032',
        'nameNode': 'hdfs://curacao:8020',
        'security_enabled': False
      }, submission.properties)


  def test_get_logical_properties(self):
    submission = Submission(self.user, fs=MockFs(logical_name='fsname'), jt=MockJt(logical_name='jtname'))

    assert_equal({'security_enabled': False}, submission.properties)

    submission._update_properties('curacao:8032', '/deployment_dir')

    assert_equal({
        'jobTracker': 'jtname',
        'nameNode': 'fsname',
        'security_enabled': False
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
        'jobTracker': 'jtaddress',
        'security_enabled': False
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

  def test_update_credentials_from_hive_action(self):

    class TestJob():
      XML_FILE_NAME = 'workflow.xml'

      def __init__(self):
        self.deployment_dir = '/tmp/test'
        self.nodes = [
            Node({'id': '1', 'type': 'hive-document', 'properties': {'jdbc_url': u'jdbc:hive2://test-replace-url:12345/default', 'password': u'test'}})
        ]

    user = User.objects.get(username='test')
    submission = Submission(user, job=TestJob(), fs=MockFs(logical_name='fsname'), jt=MockJt(logical_name='jtname'))

    finish = (
      beeswax.conf.HIVE_SERVER_HOST.set_for_testing('hue-koh-chang'),
      beeswax.conf.HIVE_SERVER_PORT.set_for_testing(12345),
    )

    try:
      creds = Credentials(credentials=TestCredentials.CREDENTIALS.copy())
      hive_properties = {
        'thrift_uri': 'thrift://first-url:9999',
        'kerberos_principal': 'hive',
        'hive2.server.principal': 'hive/hive2_host@test-realm.com',
      }

      submission.properties['credentials'] = creds.get_properties(hive_properties)
      submission._update_credentials_from_hive_action(creds)

      assert_equal(submission.properties['credentials'][creds.hiveserver2_name]['properties'], [
            ('hive2.jdbc.url', u'jdbc:hive2://test-replace-url:12345/default'),
            ('hive2.server.principal', u'hive/test-replace-url@test-realm.com')
          ]
      )

      # Test parsing failure
      hive_properties = {
        'thrift_uri': 'thrift://first-url:9999',
        'kerberos_principal': 'hive',
        'hive2.server.principal': 'hive',
      }

      submission.properties['credentials'] = creds.get_properties(hive_properties)

      assert_raises(PopupException,  submission._update_credentials_from_hive_action, creds)

    finally:
      for f in finish:
        f()

  def test_update_credentials_from_hive_action_when_jdbc_url_is_variable(self):

    class TestJob():
      XML_FILE_NAME = 'workflow.xml'

      def __init__(self):
        self.deployment_dir = '/tmp/test'
        self.nodes = [
            Node({'id': '1', 'type': 'hive-document', 'properties': {'jdbc_url': u"${wf:actionData('shell-31b5')['hiveserver']}", 'password': u'test'}})
        ]

    user = User.objects.get(username='test')
    submission = Submission(user, job=TestJob(), fs=MockFs(logical_name='fsname'), jt=MockJt(logical_name='jtname'))

    finish = (
      beeswax.conf.HIVE_SERVER_HOST.set_for_testing('hue-koh-chang'),
      beeswax.conf.HIVE_SERVER_PORT.set_for_testing(12345),
    )

    try:
      creds = Credentials(credentials=TestCredentials.CREDENTIALS.copy())
      hive_properties = {
        'thrift_uri': 'thrift://first-url:9999',
        'kerberos_principal': 'hive',
        'hive2.server.principal': 'hive/hive2_host@test-realm.com',
      }

      submission.properties['credentials'] = creds.get_properties(hive_properties)
      submission._update_credentials_from_hive_action(creds)

      assert_equal(submission.properties['credentials'][creds.hiveserver2_name]['properties'], [
            ('hive2.jdbc.url', u'jdbc:hive2://hue-koh-chang:12345/default'),
            ('hive2.server.principal', u'hive/hive2_host@test-realm.com')
          ]
      )

    finally:
      for f in finish:
        f()

  def test_generate_altus_action_start_cluster(self):

    class TestJob():
      XML_FILE_NAME = 'workflow.xml'

      def __init__(self):
        self.deployment_dir = '/tmp/test'
        self.nodes = [
            Node({'id': '1', 'type': 'hive-document', 'properties': {'jdbc_url': u"${wf:actionData('shell-31b5')['hiveserver']}", 'password': u'test'}})
        ]

    user = User.objects.get(username='test')
    submission = Submission(user, job=TestJob(), fs=MockFs(logical_name='fsname'), jt=MockJt(logical_name='jtname'))

    command = submission._generate_altus_action_script(
      service='dataeng',
      command='listClusters',
      arguments={},
      auth_key_id='altus_auth_key_id',
      auth_key_secret='altus_auth_key_secret'
    )

    assert_true('''#!/usr/bin/env python

from navoptapi.api_lib import ApiLib

hostname = 'dataengapi.us-west-1.altus.cloudera.com'
auth_key_id = 'altus_auth_key_id'
auth_key_secret = \'\'\'altus_auth_key_secret\'\'\'

def _exec(service, command, parameters=None):
  if parameters is None:
    parameters = {}

  try:
    api = ApiLib(service, hostname, auth_key_id, auth_key_secret)
    resp = api.call_api(command, parameters)
    return resp.json()
  except Exception, e:
    print e
    raise e

print _exec('dataeng', 'listClusters', {})
''' in command,
      command
    )
