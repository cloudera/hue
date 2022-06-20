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

import sys

from builtins import object
from nose.tools import assert_equal, assert_true, assert_false, assert_raises

from desktop.lib.django_test_util import make_logged_in_client
from useradmin.models import User

from notebook.connectors.spark_shell import SparkApi

if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock


class TestSparkApi(object):

  def setUp(self):
    self.client = make_logged_in_client(username="hue_test", groupname="default", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="hue_test")

    self.interpreter = {
        'name': 'livy',
        'options': {
          'api_url': 'http://gethue.com:8998'
        },
      }
    self.api = SparkApi(self.user, self.interpreter)


  def test_get_api(self):
    lang = 'pyspark'
    properties = None

    # with patch('notebook.connectors.spark_shell.get_spark_api') as get_spark_api:
    spark_api = self.api.get_api()
    assert_equal(spark_api.__class__.__name__, 'LivyClient')


  def test_get_livy_props_method(self):
    test_properties = [{
        "name": "files",
        "value": 'file_a,file_b,file_c',
      }]
    props = self.api.get_livy_props('scala', test_properties)
    assert_equal(props['files'], ['file_a', 'file_b', 'file_c'])


  def test_create_session_with_config(self):
    lang = 'pyspark'
    properties = None
    session_key = self.api._get_session_key()

    with patch('notebook.connectors.spark_shell.get_spark_api') as get_spark_api:
      with patch('notebook.connectors.spark_shell.DefaultConfiguration') as DefaultConfiguration:
        with patch('notebook.connectors.spark_shell.USE_DEFAULT_CONFIGURATION') as USE_DEFAULT_CONFIGURATION:
          DefaultConfiguration.objects.get_configuration_for_user.return_value = Mock(
                properties_list=[
                  {'multiple': False, 'name': 'driverCores', 'defaultValue': 1, 'value': 2, 'nice_name': 'Driver Cores',
                   'help_text': 'Number of cores used by the driver, only in cluster mode (Default: 1)', 'type': 'number',
                   'is_yarn': True}]
          )

          get_spark_api.return_value = Mock(
            create_session=Mock(
              return_value={'id': '1'}
            ),
            get_session=Mock(
              return_value={'state': 'idle', 'log': ''}
            )
          )
          # Case with user configuration. Expected 2 driverCores
          USE_DEFAULT_CONFIGURATION.get.return_value = True
          session = self.api.create_session(lang=lang, properties=properties)

          assert_equal(session['type'], 'pyspark')
          assert_equal(session['id'], '1')

          for p in session['properties']:
            if p['name'] == 'driverCores':
              cores = p['value']
          assert_equal(cores, 2)

          if self.api._get_session_info_from_user():
            self.api._remove_session_info_from_user()

          # Case without user configuration. Expected 1 driverCores
          USE_DEFAULT_CONFIGURATION.get.return_value = True
          DefaultConfiguration.objects.get_configuration_for_user.return_value = None
          session2 = self.api.create_session(lang=lang, properties=properties)

          assert_equal(session2['type'], 'pyspark')
          assert_equal(session2['id'], '1')

          for p in session2['properties']:
            if p['name'] == 'driverCores':
              cores = p['value']
          assert_equal(cores, 1)

          # Case with no user configuration. Expected 1 driverCores
          USE_DEFAULT_CONFIGURATION.get.return_value = False
          session3 = self.api.create_session(lang=lang, properties=properties)

          assert_equal(session3['type'], 'pyspark')
          assert_equal(session3['id'], '1')

          for p in session3['properties']:
            if p['name'] == 'driverCores':
              cores = p['value']
          assert_equal(cores, 1)


  def test_create_session_plain(self):
    lang = 'pyspark'
    properties = None
    session_key = self.api._get_session_key()

    with patch('notebook.connectors.spark_shell.get_spark_api') as get_spark_api:
      get_spark_api.return_value = Mock(
        create_session=Mock(
          return_value={'id': '1'}
        ),
        get_session=Mock(
          return_value={'state': 'idle', 'log': ''}
        )
      )

      session = self.api.create_session(lang=lang, properties=properties)

      assert_equal(session['type'], 'pyspark')
      assert_equal(session['id'], '1')

      files_properties = [prop for prop in session['properties'] if prop['name'] == 'files']
      assert_true(files_properties, session['properties'])
      assert_equal(files_properties[0]['value'], [], session['properties'])


  def test_execute(self):
    with patch('notebook.connectors.spark_shell._get_snippet_session') as _get_snippet_session:
      with patch('notebook.connectors.spark_shell.get_spark_api') as get_spark_api:
        notebook = Mock()
        snippet = {'statement': 'select * from test_table'}
        _get_snippet_session.return_value = {'id': '1'}

        get_spark_api.return_value = Mock(
          submit_statement=Mock(
            return_value={'id': 'test_id'}
          )
        )
        self.api._check_session = Mock(return_value={'id': '1'})

        response = self.api.execute(notebook, snippet)
        assert_equal(response['id'], 'test_id')

        get_spark_api.return_value = Mock(
          submit_statement=Mock()
        )
        assert_raises(Exception, self.api.execute, notebook, snippet)


  def test_check_status(self):
    with patch('notebook.connectors.spark_shell._get_snippet_session') as _get_snippet_session:
      with patch('notebook.connectors.spark_shell.get_spark_api') as get_spark_api:
        notebook = Mock()
        snippet = {
          'result': {
            'handle': {
              'id': {'test_id'}
            }
          }
        }
        _get_snippet_session.return_value = {'id': '1'}

        get_spark_api.return_value = Mock(
          fetch_data=Mock(
            return_value={'state': 'test_state'}
          )
        )
        self.api._handle_session_health_check = Mock(return_value={'id': '1'})

        response = self.api.check_status(notebook, snippet)
        assert_equal(response['status'], 'test_state')

        get_spark_api.return_value = Mock(
          submit_statement=Mock()
        )
        assert_raises(Exception, self.api.check_status, notebook, snippet)
  

  def test_get_sample_data(self):
    snippet = Mock()
    self.api._execute = Mock(
      return_value='test_value'
    )
    self.api._check_status_and_fetch_result = Mock(
      return_value={
        'data': 'test_data',
        'meta': 'test_meta'
      }
    )
    self.api.create_session = Mock(
      return_value={
        'id': 'test_id'
      }
    )

    response = self.api.get_sample_data(snippet, 'test_db', 'test_table', 'test_column')

    assert_equal(response['rows'], 'test_data')
    assert_equal(response['full_headers'], 'test_meta')
  

  def test_get_select_query(self):
    # With operation as 'hello'
    response = self.api._get_select_query('test_db', 'test_table', 'test_column', 'hello')
    assert_equal(response, "SELECT 'Hello World!'")

    # Without column name
    response = self.api._get_select_query('test_db', 'test_table')
    assert_equal(response, 'SELECT *\nFROM test_db.test_table\nLIMIT 100\n')

    # With some column name
    response = self.api._get_select_query('test_db', 'test_table', 'test_column')
    assert_equal(response, 'SELECT test_column\nFROM test_db.test_table\nLIMIT 100\n')


  def test_get_jobs(self):
    local_jobs = [
      {'url': u'http://172.21.1.246:4040/jobs/job/?id=0', 'name': u'0'}
    ]
    jobs = self.api._get_standalone_jobs(LIVY_STANDALONE_LOG)
    assert_equal(jobs, local_jobs, jobs)

    yarn_jobs = [
      {'url': u'http://huetest-1.test.com:8088/proxy/application_1444070328046_0002/', 'name': u'application_1444070328046_0002'}
    ]
    jobs = self.api._get_yarn_jobs(LIVY_YARN_LOG)
    assert_equal(jobs, yarn_jobs, jobs)



LIVY_STANDALONE_LOG = """
  Starting livy-repl on http://172.21.1.246:58449
  Using Spark's default log4j profile: org/apache/spark/log4j-defaults.properties
  15/10/05 14:02:33 INFO SparkContext: Running Spark version 1.5.0
  15/10/05 14:02:33 INFO SecurityManager: Changing view acls to: huetest
  15/10/05 14:02:33 INFO SecurityManager: Changing modify acls to: huetest
  15/10/05 14:02:33 INFO SecurityManager: SecurityManager: authentication disabled; ui acls disabled; users with view permissions: Set(huetest); users with modify permissions: Set(huetest)
  15/10/05 14:02:33 INFO Slf4jLogger: Slf4jLogger started
  15/10/05 14:02:33 INFO Remoting: Starting remoting
  15/10/05 14:02:33 INFO Remoting: Remoting started; listening on addresses :[akka.tcp://sparkDriver@172.21.1.246:58451]
  15/10/05 14:02:33 INFO Utils: Successfully started service 'sparkDriver' on port 58451.
  15/10/05 14:02:33 INFO SparkEnv: Registering MapOutputTracker
  15/10/05 14:02:33 INFO SparkEnv: Registering BlockManagerMaster
  15/10/05 14:02:33 INFO DiskBlockManager: Created local directory at /private/var/folders/7t/31vfhhq92_g628vh8q5pspbc0000gp/T/blockmgr-f63fdd28-6d86-4ae6-a91c-902fb0310fb4
  15/10/05 14:02:33 INFO MemoryStore: MemoryStore started with capacity 530.0 MB
  15/10/05 14:02:33 INFO HttpFileServer: HTTP File server directory is /private/var/folders/7t/31vfhhq92_g628vh8q5pspbc0000gp/T/spark-a0e35333-e2be-4b83-8a7e-3cb468270dc2/httpd-0235b01f-ee8b-40fd-96a9-de946b1a3426
  15/10/05 14:02:33 INFO HttpServer: Starting HTTP Server
  15/10/05 14:02:33 INFO Utils: Successfully started service 'HTTP file server' on port 58452.
  15/10/05 14:02:33 INFO SparkEnv: Registering OutputCommitCoordinator
  15/10/05 14:02:33 INFO Utils: Successfully started service 'SparkUI' on port 4040.
  15/10/05 14:02:33 INFO SparkUI: Started SparkUI at http://172.21.1.246:4040
  15/10/05 14:02:34 INFO SparkContext: Added JAR file:/Users/huetest/Dev/hue/apps/spark/java/livy-assembly/target/scala-2.10/livy-assembly-3.9.0-SNAPSHOT.jar at http://172.21.1.246:58452/jars/livy-assembly-3.9.0-SNAPSHOT.jar with timestamp 1444078954103
  15/10/05 14:02:34 WARN MetricsSystem: Using default name DAGScheduler for source because spark.app.id is not set.
  15/10/05 14:02:34 INFO Executor: Starting executor ID driver on host localhost
  15/10/05 14:02:34 INFO Utils: Successfully started service 'org.apache.spark.network.netty.NettyBlockTransferService' on port 58453.
  15/10/05 14:02:34 INFO NettyBlockTransferService: Server created on 58453
  15/10/05 14:02:34 INFO BlockManagerMaster: Trying to register BlockManager
  15/10/05 14:02:34 INFO BlockManagerMasterEndpoint: Registering block manager localhost:58453 with 530.0 MB RAM, BlockManagerId(driver, localhost, 58453)
  15/10/05 14:02:34 INFO BlockManagerMaster: Registered BlockManager
  15/10/05 14:02:36 INFO MemoryStore: ensureFreeSpace(130448) called with curMem=0, maxMem=555755765
  15/10/05 14:02:36 INFO MemoryStore: Block broadcast_0 stored as values in memory (estimated size 127.4 KB, free 529.9 MB)
  15/10/05 14:02:36 INFO MemoryStore: ensureFreeSpace(14276) called with curMem=130448, maxMem=555755765
  15/10/05 14:02:36 INFO MemoryStore: Block broadcast_0_piece0 stored as bytes in memory (estimated size 13.9 KB, free 529.9 MB)
  15/10/05 14:02:36 INFO BlockManagerInfo: Added broadcast_0_piece0 in memory on localhost:58453 (size: 13.9 KB, free: 530.0 MB)
  15/10/05 14:02:36 INFO SparkContext: Created broadcast 0 from textFile at NativeMethodAccessorImpl.java:-2
  15/10/05 14:02:36 INFO FileInputFormat: Total input paths to process : 1
  15/10/05 14:02:36 INFO SparkContext: Starting job: collect at <stdin>:1
  15/10/05 14:02:36 INFO DAGScheduler: Registering RDD 3 (reduceByKey at <stdin>:1)
  15/10/05 14:02:36 INFO DAGScheduler: Registering RDD 7 (combineByKey at <stdin>:3)
  15/10/05 14:02:36 INFO DAGScheduler: Got job 0 (collect at <stdin>:1) with 2 output partitions
  15/10/05 14:02:36 INFO DAGScheduler: Final stage: ResultStage 2(collect at <stdin>:1)
  15/10/05 14:02:36 INFO DAGScheduler: Parents of final stage: List(ShuffleMapStage 1)
  15/10/05 14:02:36 INFO DAGScheduler: Missing parents: List(ShuffleMapStage 1)
  15/10/05 14:02:36 INFO DAGScheduler: Submitting ShuffleMapStage 0 (PairwiseRDD[3] at reduceByKey at <stdin>:1), which has no missing parents
  15/10/05 14:02:36 INFO MemoryStore: ensureFreeSpace(8960) called with curMem=144724, maxMem=555755765
  15/10/05 14:02:36 INFO MemoryStore: Block broadcast_1 stored as values in memory (estimated size 8.8 KB, free 529.9 MB)
  15/10/05 14:02:36 INFO MemoryStore: ensureFreeSpace(5483) called with curMem=153684, maxMem=555755765
  15/10/05 14:02:36 INFO MemoryStore: Block broadcast_1_piece0 stored as bytes in memory (estimated size 5.4 KB, free 529.9 MB)
  15/10/05 14:02:36 INFO BlockManagerInfo: Added broadcast_1_piece0 in memory on localhost:58453 (size: 5.4 KB, free: 530.0 MB)
  15/10/05 14:02:36 INFO SparkContext: Created broadcast 1 from broadcast at DAGScheduler.scala:861
  15/10/05 14:02:36 INFO DAGScheduler: Submitting 2 missing tasks from ShuffleMapStage 0 (PairwiseRDD[3] at reduceByKey at <stdin>:1)
  15/10/05 14:02:36 INFO TaskSchedulerImpl: Adding task set 0.0 with 2 tasks
  15/10/05 14:02:36 INFO TaskSetManager: Starting task 0.0 in stage 0.0 (TID 0, localhost, PROCESS_LOCAL, 2266 bytes)
  15/10/05 14:02:36 INFO TaskSetManager: Starting task 1.0 in stage 0.0 (TID 1, localhost, PROCESS_LOCAL, 2266 bytes)
  15/10/05 14:02:36 INFO Executor: Running task 0.0 in stage 0.0 (TID 0)
  15/10/05 14:02:36 INFO Executor: Running task 1.0 in stage 0.0 (TID 1)
  15/10/05 14:02:36 INFO Executor: Fetching http://172.21.1.246:58452/jars/livy-assembly-3.9.0-SNAPSHOT.jar with timestamp 1444078954103
  15/10/05 14:02:36 INFO Utils: Fetching http://172.21.1.246:58452/jars/livy-assembly-3.9.0-SNAPSHOT.jar to /private/var/folders/7t/31vfhhq92_g628vh8q5pspbc0000gp/T/spark-a0e35333-e2be-4b83-8a7e-3cb468270dc2/userFiles-d0940846-b38a-4e4d-af07-8419b364d7ff/fetchFileTemp476551478197543813.tmp
  15/10/05 14:02:36 INFO Executor: Adding file:/private/var/folders/7t/31vfhhq92_g628vh8q5pspbc0000gp/T/spark-a0e35333-e2be-4b83-8a7e-3cb468270dc2/userFiles-d0940846-b38a-4e4d-af07-8419b364d7ff/livy-assembly-3.9.0-SNAPSHOT.jar to class loader
  15/10/05 14:02:36 INFO HadoopRDD: Input split: file:/Users/huetest/Downloads/babs_open_data_year_1/201402_babs_open_data/201402_trip_data.csv:0+8609511
  15/10/05 14:02:36 INFO HadoopRDD: Input split: file:/Users/huetest/Downloads/babs_open_data_year_1/201402_babs_open_data/201402_trip_data.csv:8609511+8609511
  15/10/05 14:02:36 INFO deprecation: mapred.tip.id is deprecated. Instead, use mapreduce.task.id
  15/10/05 14:02:36 INFO deprecation: mapred.task.id is deprecated. Instead, use mapreduce.task.attempt.id
  15/10/05 14:02:36 INFO deprecation: mapred.task.is.map is deprecated. Instead, use mapreduce.task.ismap
  15/10/05 14:02:36 INFO deprecation: mapred.task.partition is deprecated. Instead, use mapreduce.task.partition
  15/10/05 14:02:36 INFO deprecation: mapred.job.id is deprecated. Instead, use mapreduce.job.id
  15/10/05 14:02:37 INFO PythonRDD: Times: total = 727, boot = 229, init = 44, finish = 454
  15/10/05 14:02:37 INFO PythonRDD: Times: total = 730, boot = 226, init = 46, finish = 458
  15/10/05 14:02:37 INFO Executor: Finished task 1.0 in stage 0.0 (TID 1). 2318 bytes result sent to driver
  15/10/05 14:02:37 INFO Executor: Finished task 0.0 in stage 0.0 (TID 0). 2318 bytes result sent to driver
  15/10/05 14:02:37 INFO TaskSetManager: Finished task 1.0 in stage 0.0 (TID 1) in 950 ms on localhost (1/2)
  15/10/05 14:02:37 INFO TaskSetManager: Finished task 0.0 in stage 0.0 (TID 0) in 962 ms on localhost (2/2)
  15/10/05 14:02:37 INFO TaskSchedulerImpl: Removed TaskSet 0.0, whose tasks have all completed, from pool
  15/10/05 14:02:37 INFO DAGScheduler: ShuffleMapStage 0 (reduceByKey at <stdin>:1) finished in 0.973 s
  15/10/05 14:02:37 INFO DAGScheduler: looking for newly runnable stages
"""
LIVY_YARN_LOG = """
  15/10/05 13:51:21 INFO client.RMProxy: Connecting to ResourceManager at huetest-1.test.com/175.18.213.12:8032
  15/10/05 13:51:21 INFO yarn.Client: Requesting a new application from cluster with 3 NodeManagers
  15/10/05 13:51:21 INFO yarn.Client: Verifying our application has not requested more than the maximum memory capability of the cluster (2048 MB per container)
  15/10/05 13:51:21 INFO yarn.Client: Will allocate AM container, with 1408 MB memory including 384 MB overhead
  15/10/05 13:51:21 INFO yarn.Client: Setting up container launch context for our AM
  15/10/05 13:51:21 INFO yarn.Client: Setting up the launch environment for our AM container
  15/10/05 13:51:21 INFO yarn.Client: Preparing resources for our AM container
  15/10/05 13:51:21 WARN util.NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
  15/10/05 13:51:21 INFO yarn.Client: Uploading resource file:/Users/huetest/Dev/spark-1.5.0-bin-hadoop2.6/lib/spark-assembly-1.5.0-hadoop2.6.0.jar -> hdfs://huetest-1.vpc.cloudera.com:8020/user/huetest/.sparkStaging/application_1444070328046_0002/spark-assembly-1.5.0-hadoop2.6.0.jar
  15/10/05 13:52:00 INFO yarn.Client: Uploading resource file:/Users/huetest/Dev/hue/apps/spark/java/livy-assembly/target/scala-2.10/livy-assembly-3.9.0-SNAPSHOT.jar -> hdfs://huetest-1.vpc.cloudera.com:8020/user/huetest/.sparkStaging/application_1444070328046_0002/livy-assembly-3.9.0-SNAPSHOT.jar
  15/10/05 13:52:09 INFO yarn.Client: Uploading resource file:/Users/huetest/Dev/spark-1.5.0-bin-hadoop2.6/python/lib/pyspark.zip -> hdfs://huetest-1.vpc.cloudera.com:8020/user/huetest/.sparkStaging/application_1444070328046_0002/pyspark.zip
  15/10/05 13:52:09 INFO yarn.Client: Uploading resource file:/Users/huetest/Dev/spark-1.5.0-bin-hadoop2.6/python/lib/py4j-0.8.2.1-src.zip -> hdfs://huetest-1.vpc.cloudera.com:8020/user/huetest/.sparkStaging/application_1444070328046_0002/py4j-0.8.2.1-src.zip
  15/10/05 13:52:10 INFO yarn.Client: Uploading resource file:/private/var/folders/7t/31vfhhq92_g628vh8q5pspbc0000gp/T/spark-3bde33db-374c-4abe-a4af-704bd5dc09d2/__spark_conf__4420686202746650998.zip -> hdfs://huetest-1.vpc.cloudera.com:8020/user/huetest/.sparkStaging/application_1444070328046_0002/__spark_conf__4420686202746650998.zip
  15/10/05 13:52:10 INFO spark.SecurityManager: Changing view acls to: huetest
  15/10/05 13:52:10 INFO spark.SecurityManager: Changing modify acls to: huetest
  15/10/05 13:52:10 INFO spark.SecurityManager: SecurityManager: authentication disabled; ui acls disabled; users with view permissions: Set(huetest); users with modify permissions: Set(huetest)
  15/10/05 13:52:10 INFO yarn.Client: Submitting application 2 to ResourceManager
  15/10/05 13:52:10 INFO impl.YarnClientImpl: Submitted application application_1444070328046_0002
  15/10/05 13:52:11 INFO yarn.Client: Application report for application_1444070328046_0002 (state: ACCEPTED)
  15/10/05 13:52:11 INFO yarn.Client:
        client token: N/A
        diagnostics: N/A
        ApplicationMaster host: N/A
        ApplicationMaster RPC port: -1
        queue: root.huetest
        start time: 1444078329419
        final status: UNDEFINED
        tracking URL: http://huetest-1.test.com:8088/proxy/application_1444070328046_0002/
        user: huetest
  15/10/05 13:52:12 INFO yarn.Client: Application report for application_1444070328046_0002 (state: ACCEPTED)
  15/10/05 13:52:13 INFO yarn.Client: Application report for application_1444070328046_0002 (state: ACCEPTED)
  15/10/05 13:52:14 INFO yarn.Client: Application report for application_1444070328046_0002 (state: ACCEPTED)
  15/10/05 13:52:16 INFO yarn.Client: Application report for application_1444070328046_0002 (state: ACCEPTED)
  15/10/05 13:52:17 INFO yarn.Client: Application report for application_1444070328046_0002 (state: ACCEPTED)
  15/10/05 13:52:18 INFO yarn.Client: Application report for application_1444070328046_0002 (state: ACCEPTED)
  15/10/05 13:52:19 INFO yarn.Client: Application report for application_1444070328046_0002 (state: ACCEPTED)
  15/10/05 13:52:20 INFO yarn.Client: Application report for application_1444070328046_0002 (state: ACCEPTED)
  15/10/05 13:52:21 INFO yarn.Client: Application report for application_1444070328046_0002 (state: ACCEPTED)
  15/10/05 13:52:22 INFO yarn.Client: Application report for application_1444070328046_0002 (state: ACCEPTED)
  15/10/05 13:52:23 INFO yarn.Client: Application report for application_1444070328046_0002 (state: RUNNING)
  15/10/05 13:52:23 INFO yarn.Client:
        client token: N/A
        diagnostics: N/A
        ApplicationMaster host: 175.18.213.12
        ApplicationMaster RPC port: 0
        queue: root.huetest
        start time: 1444078329419
        final status: UNDEFINED
        tracking URL: http://huetest-1.test.com:8088/proxy/application_1444070328046_0002/
        user: huetest
  15/10/05 13:52:24 INFO yarn.Client: Application report for application_1444070328046_0002 (state: RUNNING)
"""
