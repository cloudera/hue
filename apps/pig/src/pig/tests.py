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
import time

from django.contrib.auth.models import User
from django.urls import reverse

from nose.plugins.skip import SkipTest
from nose.tools import assert_true, assert_equal, assert_false

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access
from desktop.models import SAMPLE_USER_ID
from hadoop import pseudo_hdfs4
from hadoop.pseudo_hdfs4 import is_live_cluster
from liboozie.oozie_api_tests import OozieServerProvider
from liboozie.conf import SECURITY_ENABLED

from oozie.tests import OozieBase

from pig.models import create_or_update_script, PigScript
from pig.api import OozieApi, get


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


class TestMock(TestPigBase):

  def test_create_script(self):
    pig_script = self.create_script()
    assert_equal('Test', pig_script.dict['name'])

  def test_check_hcatalogs_sharelib(self):
    api = get(None, None, self.user)
    pig_script = self.create_script()

    # Regular
    wf = api._create_workflow(pig_script, '[]')
    assert_false({'name': u'oozie.action.sharelib.for.pig', 'value': u'pig,hcatalog,hive'} in wf.find_all_parameters(), wf.find_all_parameters())

    # With HCat
    pig_script.update_from_dict({
        'script':"""
           a = LOAD 'sample_07' USING org.apache.hcatalog.pig.HCatLoader();
           dump a;
    """})
    pig_script.save()

    wf = api._create_workflow(pig_script, '[]')
    assert_true({'name': u'oozie.action.sharelib.for.pig', 'value': u'pig,hcatalog,hive'} in wf.find_all_parameters(), wf.find_all_parameters())

    start_link = wf.start.get_link()
    pig_action = start_link.child
    assert_equal([], pig_action.credentials)

  def test_check_automated_hcatalogs_credentials(self):
    reset = SECURITY_ENABLED.set_for_testing(True)

    try:
      api = get(None, None, self.user)
      pig_script = self.create_script()
      pig_script.update_from_dict({
          'script':"""
            a = LOAD 'sample_07' USING org.apache.hcatalog.pig.HCatLoader();
            dump a;

            STORE raw_data INTO 'students' USING
            org.apache.pig.backend.hadoop.hbase.HBaseStorage
            org.apache.pig.backend.hadoop.hbase.HBaseStorage (
            'info:first_name info:last_name info:age info:gpa info:part');
            raw_data = LOAD 'students' USING PigStorage( ' ' ) AS (
            id: chararray,
            first_name: chararray,
            last_name: chararray,
            age: int,
            gpa: float,
            part: int );
      """})
      pig_script.save()

      wf = api._create_workflow(pig_script, '[]')
      start_link = wf.start.get_link()
      pig_action = start_link.child
      assert_equal([{u'name': u'hcat', u'value': True}, {u'name': u'hbase', u'value': True}], pig_action.credentials)
    finally:
      reset()


  def test_editor_view(self):
    response = self.c.get(reverse('pig:app'))
    assert_true('Unsaved script' in response.content)

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

  def parse_oozie_logs(self):
    api = get(None, None, self.user)

    assert_equal(
'''Run pig script using PigRunner.run() for Pig version 0.8+
  Apache Pig version 0.11.0-cdh4.4.0-SNAPSHOT (rexported)
  compiled Jun 30 2013, 03:40:22

  Run pig script using PigRunner.run() for Pig version 0.8+
  2013-10-09 17:30:39,709 [main] INFO  org.apache.pig.Main  - Apache Pig version 0.11.0-cdh4.4.0-SNAPSHOT (rexported) compiled Jun 30 2013, 03:40:22
  2013-10-09 17:30:39,709 [main] INFO  org.apache.pig.Main  - Apache Pig version 0.11.0-cdh4.4.0-SNAPSHOT (rexported) compiled Jun 30 2013, 03:40:22
  2013-10-09 17:30:39,710 [main] INFO  org.apache.pig.Main  - Logging error messages to: /var/lib/hadoop-yarn/cache/yarn/nm-local-dir/usercache/romain/appcache/application_1381360805876_0001/container_1381360805876_0001_01_000002/pig-job_1381360805876_0001.log
  2013-10-09 17:30:39,710 [main] INFO  org.apache.pig.Main  - Logging error messages to: /var/lib/hadoop-yarn/cache/yarn/nm-local-dir/usercache/romain/appcache/application_1381360805876_0001/container_1381360805876_0001_01_000002/pig-job_1381360805876_0001.log
  2013-10-09 17:30:39,739 [main] WARN  org.apache.hadoop.conf.Configuration  - dfs.df.interval is deprecated. Instead, use fs.df.interval
  2013-10-09 17:30:39,739 [main] WARN  org.apache.hadoop.conf.Configuration  - mapred.task.tracker.http.address is deprecated. Instead, use mapreduce.tasktracker.http.address
  2013-10-09 17:30:39,833 [main] INFO  org.apache.pig.backend.hadoop.executionengine.HExecutionEngine  - Connecting to map-reduce job tracker at: localhost:8032
  hdfs://localhost:8020/user/romain/.Trash  <dir>
  hdfs://localhost:8020/user/romain/examples  <dir>
  hdfs://localhost:8020/user/romain/tweets  <dir>
  hdfs://localhost:8020/user/romain/wordcount.jar<r 1>  3165
  hdfs://localhost:8020/user/romain/words  <dir>
  hdfs://localhost:8020/user/romain/yelp  <dir>''', api._match_logs({'logs': [None, OOZIE_LOGS]}))


class TestWithHadoop(OozieBase):

  def setUp(self):
    super(TestWithHadoop, self).setUp()
    # FIXME (HUE-2562): The tests unfortunately require superuser at the
    # moment, but should be rewritten to not need it.
    self.c = make_logged_in_client(is_superuser=True)
    grant_access("test", "test", "pig")
    self.user = User.objects.get(username='test')
    self.c.post(reverse('pig:install_examples'))

    self.cluster = pseudo_hdfs4.shared_cluster()
    self.api = OozieApi(self.cluster.fs, self.cluster.jt, self.user)

  def test_create_workflow(self):
    xattrs = {
      'parameters': [
        {'name': 'output', 'value': self.cluster.fs_prefix + '/test_pig_script_workflow'},
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

    output_path = self.cluster.fs_prefix + '/test_pig_script_2'
    params = json.dumps([
      {'name': 'output', 'value': output_path},
    ])

    workflow = self.api._create_workflow(pig_script, params)
    pig_action = workflow.start.get_child('to').get_full_node()

    assert_equal([
        {u'type': u'argument', u'value': u'-param'}, {u'type': u'argument', u'value': u'output=%s' % output_path},
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

      self.api.stop(job_id)

      raise Exception(msg)

    return pig_script_id

OOZIE_LOGS ="""  Log Type: stdout

  Log Length: 117627

  Oozie Launcher starts

  Heart beat
  Starting the execution of prepare actions
  Completed the execution of prepare actions successfully

  Files in current dir:/var/lib/hadoop-yarn/cache/yarn/nm-local-dir/usercache/romain/appcache/application_1381360805876_0001/container_1381360805876_0001_01_000002/.
  ======================
  File: commons-cli-1.2.jar
  File: antlr-runtime-3.4.jar
  File: stringtemplate-3.2.1.jar
  File: script.pig
  File: jyson-1.0.2.jar

  Oozie Java/Map-Reduce/Pig action launcher-job configuration
  =================================================================
  Workflow job id   : 0000000-131009162028638-oozie-oozi-W
  Workflow action id: 0000000-131009162028638-oozie-oozi-W@pig

  Classpath         :
  ------------------------
  /var/lib/hadoop-yarn/cache/yarn/nm-local-dir/usercache/romain/appcache/application_1381360805876_0001/container_1381360805876_0001_01_000002
  /etc/hadoop/conf
  /usr/lib/hadoop/hadoop-nfs-2.1.0-cdh5.0.0-SNAPSHOT.jar
  /usr/lib/hadoop/hadoop-common-2.1.0-cdh5.0.0-SNAPSHOT.jar
  /usr/lib/hadoop/hadoop-auth-2.1.0-cdh5.0.0-SNAPSHOT.jar
  /usr/lib/hadoop/hadoop-common.jar
  /var/lib/hadoop-yarn/cache/yarn/nm-local-dir/usercache/romain/appcache/application_1381360805876_0001/container_1381360805876_0001_01_000002/jyson-1.0.2.jar
  ------------------------

  Main class        : org.apache.oozie.action.hadoop.PigMain

  Maximum output    : 2048

  Arguments         :

  Java System Properties:
  ------------------------
  #
  #Wed Oct 09 17:30:39 PDT 2013
  java.runtime.name=Java(TM) SE Runtime Environment
  awt.toolkit=sun.awt.X11.XToolkit
  java.vm.info=mixed mode
  java.version=1.7.0_40
  java.ext.dirs=/usr/lib/jvm/java-7-oracle/jre/lib/ext\:/usr/java/packages/lib/ext
  sun.boot.class.path=/usr/lib/jvm/java-7-oracle/jre/lib/resources.jar\:/usr/lib/jvm/java-7-oracle/jre/lib/rt.jar\:/usr/lib/jvm/java-7-oracle/jre/lib/sunrsasign.jar\:/usr/lib/jvm/java-7-oracle/jre/lib/jsse.jar\:/usr/lib/jvm/java-7-oracle/jre/lib/jce.jar\:/usr/lib/jvm/java-7-oracle/jre/lib/charsets.jar\:/usr/lib/jvm/java-7-oracle/jre/lib/jfr.jar\:/usr/lib/jvm/java-7-oracle/jre/classes
  java.vendor=Oracle Corporation
  file.separator=/
  oozie.launcher.job.id=job_1381360805876_0001
  oozie.action.stats.properties=/var/lib/hadoop-yarn/cache/yarn/nm-local-dir/usercache/romain/appcache/application_1381360805876_0001/container_1381360805876_0001_01_000002/stats.properties
  java.vendor.url.bug=http\://bugreport.sun.com/bugreport/
  sun.io.unicode.encoding=UnicodeLittle
  sun.cpu.endian=little
  sun.cpu.isalist=
  ------------------------

  =================================================================

  >>> Invoking Main class now >>>


  Oozie Pig action configuration
  =================================================================
  ------------------------
  Setting env property for mapreduce.job.credentials.binary to:/var/lib/hadoop-yarn/cache/yarn/nm-local-dir/usercache/romain/appcache/application_1381360805876_0001/container_1381360805876_0001_01_000002/container_tokens
  ------------------------
  pig.properties:
  --------------------
  mapreduce.job.ubertask.enable : false
  yarn.resourcemanager.max-completed-applications : 10000
  yarn.resourcemanager.delayed.delegation-token.removal-interval-ms : 30000
  yarn.nodemanager.delete.debug-delay-sec : 0
  hadoop.ssl.require.client.cert : false
  dfs.datanode.max.transfer.threads : 4096
  --------------------

  Pig script [script.pig] content:
  ------------------------
  ls
  ------------------------

  Current (local) dir = /var/lib/hadoop-yarn/cache/yarn/nm-local-dir/usercache/romain/appcache/application_1381360805876_0001/container_1381360805876_0001_01_000002
  Pig command arguments :
  -file
  script.pig
  -log4jconf
  /var/lib/hadoop-yarn/cache/yarn/nm-local-dir/usercache/romain/appcache/application_1381360805876_0001/container_1381360805876_0001_01_000002/piglog4j.properties
  -logfile
  pig-job_1381360805876_0001.log
  =================================================================

  >>> Invoking Pig command line now >>>


  Run pig script using PigRunner.run() for Pig version 0.8+
  Apache Pig version 0.11.0-cdh4.4.0-SNAPSHOT (rexported)
  compiled Jun 30 2013, 03:40:22

  Run pig script using PigRunner.run() for Pig version 0.8+
  2013-10-09 17:30:39,709 [main] INFO  org.apache.pig.Main  - Apache Pig version 0.11.0-cdh4.4.0-SNAPSHOT (rexported) compiled Jun 30 2013, 03:40:22
  2013-10-09 17:30:39,709 [main] INFO  org.apache.pig.Main  - Apache Pig version 0.11.0-cdh4.4.0-SNAPSHOT (rexported) compiled Jun 30 2013, 03:40:22
  2013-10-09 17:30:39,710 [main] INFO  org.apache.pig.Main  - Logging error messages to: /var/lib/hadoop-yarn/cache/yarn/nm-local-dir/usercache/romain/appcache/application_1381360805876_0001/container_1381360805876_0001_01_000002/pig-job_1381360805876_0001.log
  2013-10-09 17:30:39,710 [main] INFO  org.apache.pig.Main  - Logging error messages to: /var/lib/hadoop-yarn/cache/yarn/nm-local-dir/usercache/romain/appcache/application_1381360805876_0001/container_1381360805876_0001_01_000002/pig-job_1381360805876_0001.log
  2013-10-09 17:30:39,739 [main] WARN  org.apache.hadoop.conf.Configuration  - dfs.df.interval is deprecated. Instead, use fs.df.interval
  2013-10-09 17:30:39,739 [main] WARN  org.apache.hadoop.conf.Configuration  - mapred.task.tracker.http.address is deprecated. Instead, use mapreduce.tasktracker.http.address
  2013-10-09 17:30:39,833 [main] INFO  org.apache.pig.backend.hadoop.executionengine.HExecutionEngine  - Connecting to map-reduce job tracker at: localhost:8032
  hdfs://localhost:8020/user/romain/.Trash  <dir>
  hdfs://localhost:8020/user/romain/examples  <dir>
  hdfs://localhost:8020/user/romain/tweets  <dir>
  hdfs://localhost:8020/user/romain/wordcount.jar<r 1>  3165
  hdfs://localhost:8020/user/romain/words  <dir>
  hdfs://localhost:8020/user/romain/yelp  <dir>

  <<< Invocation of Pig command completed <<<

  Hadoop Job IDs executed by Pig:


  <<< Invocation of Main class completed <<<


  Oozie Launcher ends

  2013-10-09 17:30:40,009 [main] INFO  org.apache.hadoop.mapred.Task  - Task:attempt_1381360805876_0001_m_000000_0 is done. And is in the process of committing
  2013-10-09 17:30:40,087 [main] INFO  org.apache.hadoop.mapred.Task  - Task attempt_1381360805876_0001_m_000000_0 is allowed to commit now
  2013-10-09 17:30:40,094 [main] INFO  org.apache.hadoop.mapreduce.lib.output.FileOutputCommitter  - Saved output of task 'attempt_1381360805876_0001_m_000000_0' to hdfs://localhost:8020/user/romain/oozie-oozi/0000000-131009162028638-oozie-oozi-W/pig--pig/output/_temporary/1/task_1381360805876_0001_m_000000
  2013-10-09 17:30:40,153 [main] INFO  org.apache.hadoop.mapred.Task  - Task 'attempt_1381360805876_0001_m_000000_0' done.
  2013-10-09 17:30:40,254 [main] INFO  org.apache.hadoop.metrics2.impl.MetricsSystemImpl  - Stopping MapTask metrics system...
  2013-10-09 17:30:40,257 [main] INFO  org.apache.hadoop.metrics2.impl.MetricsSystemImpl  - MapTask metrics system stopped.
  2013-10-09 17:30:40,257 [main] INFO  org.apache.hadoop.metrics2.impl.MetricsSystemImpl  - MapTask metrics system shutdown complete.
"""
