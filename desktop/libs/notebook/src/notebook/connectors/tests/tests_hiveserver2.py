#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import logging
import re
import time

from nose.plugins.skip import SkipTest
from nose.tools import assert_equal, assert_true

from django.contrib.auth.models import User
from django.urls import reverse

from desktop.lib.i18n import smart_str
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import add_to_group, grant_access
from hadoop.pseudo_hdfs4 import is_live_cluster

from notebook.api import _save_notebook
from notebook.connectors.hiveserver2 import HS2Api
from notebook.models import make_notebook, Notebook

from beeswax.server import dbms
from beeswax.test_base import BeeswaxSampleProvider, get_query_server_config, is_hive_on_spark


LOG = logging.getLogger(__name__)


class TestHiveserver2Api(object):

  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="test", recreate=False, is_superuser=False)
    self.user = User.objects.get(username='test')

    add_to_group('test')
    grant_access("test", "test", "notebook")
    grant_access("test", "test", "hive")

    self.db = dbms.get(self.user, get_query_server_config())
    self.api = HS2Api(self.user)


  def test_prepare_hql_query(self):
    statement = "SELECT myUpper(description) FROM sample_07 LIMIT 10"
    snippet_json = """
        {
            "status": "running",
            "database": "default",
            "properties": {
                "files": [],
                "functions": [{
                    "class_name": "org.hue.udf.MyUpper",
                    "name": "myUpper"
                }],
                "settings": []
            },
            "result": {
                "handle": {
                    "log_context": null,
                    "statements_count": 1,
                    "statement_id": 0,
                    "has_more_statements": false,
                    "secret": "UVZXF/qtTQumumz0Q8tNDQ==",
                    "has_result_set": true,
                    "operation_type": 0,
                    "modified_row_count": null,
                    "guid": "ZxOd4IjqTeK1PUTq+MdcDA=="
                },
                "type": "table",
                "id": "ae81b805-dcf1-9692-0452-797681e997ed"
            },
            "statement": "%(statement)s",
            "type": "hive",
            "id": "9b50e364-f7b2-303d-e924-db8b0bd9866d"
        }
    """ % {'statement': statement}
    session_json = """
            {
                "type": "hive",
                "properties": [
                    {
                        "multiple": true,
                        "value": [
                            {
                                "path": "/user/test/myudfs.jar",
                                "type": "jar"
                            }
                        ],
                        "nice_name": "Files",
                        "key": "files",
                        "help_text": "Add one or more files, jars, or archives to the list of resources.",
                        "type": "hdfs-files"
                    },
                    {
                        "multiple": true,
                        "value": [
                            {
                                "class_name": "org.hue.udf.MyUpper",
                                "name": "myUpper"
                            }
                        ],
                        "nice_name": "Functions",
                        "key": "functions",
                        "help_text": "Add one or more registered UDFs (requires function name and fully-qualified class name).",
                        "type": "functions"
                    },
                    {
                        "multiple": true,
                        "value": [
                            {
                                "value": "spark",
                                "key": "hive.execution.engine"
                            }
                        ],
                        "nice_name": "Settings",
                        "key": "settings",
                        "help_text": "Hive and Hadoop configuration properties.",
                        "type": "settings",
                        "options": [
                            "hive.map.aggr",
                            "hive.exec.compress.output",
                            "hive.exec.parallel",
                            "hive.execution.engine",
                            "mapreduce.job.queuename"
                        ]
                    }
                ],
                "id": 30
            }
    """

    snippet = json.loads(snippet_json)
    session = json.loads(session_json)
    hql_query = self.api._prepare_hql_query(snippet, statement, session)

    assert_equal([{'key': 'hive.execution.engine', 'value': 'spark'}], hql_query.settings)
    assert_equal([{'type': 'jar', 'path': '/user/test/myudfs.jar'}], hql_query.file_resources)
    assert_equal([{'name': 'myUpper', 'class_name': 'org.hue.udf.MyUpper'}], hql_query.functions)

    config_statements = ', '.join(hql_query.get_configuration_statements())

    pattern = re.compile("ADD JAR hdfs://[A-Za-z0-9.:_-]+/user/test/myudfs.jar")
    assert_true(pattern.search(config_statements), config_statements)
    assert_true("CREATE TEMPORARY FUNCTION myUpper AS 'org.hue.udf.MyUpper'" in config_statements, config_statements)


  def test_upgrade_properties(self):
    properties = None
    # Verify that upgrade will return defaults if current properties not formatted as settings
    upgraded_props = self.api.upgrade_properties(lang='hive', properties=properties)
    assert_equal(upgraded_props, self.api.get_properties(lang='hive'))

    # Verify that upgrade will save old properties and new settings
    properties = [
        {
            'key': 'hive.execution.engine',
            'value': 'mr'
        },
        {
            'key': 'hive.exec.compress.output',
            'value': False
        }
    ]
    upgraded_props = self.api.upgrade_properties(lang='hive', properties=properties)
    settings = next((prop for prop in upgraded_props if prop['key'] == 'settings'), None)
    assert_equal(settings['value'], properties)

    # Verify that already upgraded properties will be unchanged
    properties = [
        {
            "multiple": True,
            "value": [],
            "nice_name": "Files",
            "key": "files",
            "help_text": "Add one or more files, jars, or archives to the list of resources.",
            "type": "hdfs-files"
        },
        {
            "multiple": True,
            "value": [],
            "nice_name": "Functions",
            "key": "functions",
            "help_text": "Add one or more registered UDFs (requires function name and fully-qualified class name).",
            "type": "functions"
        },
        {
            "multiple": True,
            "value": [
                {
                    "key": "hive.execution.engine",
                    "value": "spark"
                }
            ],
            "nice_name": "Settings",
            "key": "settings",
            "help_text": "Hive and Hadoop configuration properties.",
            "type": "settings",
            "options": [
                "hive.map.aggr",
                "hive.exec.compress.output",
                "hive.exec.parallel",
                "hive.execution.engine",
                "mapreduce.job.queuename"
            ]
        }
    ]
    upgraded_props = self.api.upgrade_properties(lang='hive', properties=properties)
    assert_equal(upgraded_props, properties)


  def test_progress(self):
    snippet = json.loads("""
        {
            "status": "running",
            "database": "default",
            "id": "d70d31ee-a62a-4854-b2b1-b852f6a390f5",
            "result": {
                "type": "table",
                "handle": {
                  "statement_id": 0,
                  "statements_count": 2,
                  "has_more_statements": true
                },
                "id": "ca11fcb1-11a5-f534-8200-050c8e1e57e3"
            },
            "statement": "%(statement)s",
            "type": "hive",
            "properties": {
                "files": [],
                "functions": [],
                "settings": []
            }
        }
      """ % {'statement': "SELECT * FROM sample_07;"}
    )

    logs = """INFO  : Compiling command(queryId=hive_20160620133030_7e69739c-a00b-4170-8717-9eee331130eb): SELECT app,
                 AVG(bytes) AS avg_bytes
        FROM web_logs
        GROUP BY  app
        HAVING app IS NOT NULL
        ORDER BY avg_bytes DESC
        INFO  : Semantic Analysis Completed
        INFO  : Returning Hive schema: Schema(fieldSchemas:[FieldSchema(name:app, type:string, comment:null), FieldSchema(name:avg_bytes, type:double, comment:null)], properties:null)
        INFO  : Completed compiling command(queryId=hive_20160620133030_7e69739c-a00b-4170-8717-9eee331130eb); Time taken: 0.116 seconds
        INFO  : Executing command(queryId=hive_20160620133030_7e69739c-a00b-4170-8717-9eee331130eb): SELECT app,
                 AVG(bytes) AS avg_bytes
        FROM web_logs
        GROUP BY  app
        HAVING app IS NOT NULL
        ORDER BY avg_bytes DESC
        INFO  : Query ID = hive_20160620133030_7e69739c-a00b-4170-8717-9eee331130eb
        INFO  : Total jobs = 2
        INFO  : Launching Job 1 out of 2
        INFO  : Starting task [Stage-1:MAPRED] in serial mode
        INFO  : Number of reduce tasks not specified. Estimated from input data size: 1
        INFO  : In order to change the average load for a reducer (in bytes):
        INFO  :   set hive.exec.reducers.bytes.per.reducer=<number>
        INFO  : In order to limit the maximum number of reducers:
        INFO  :   set hive.exec.reducers.max=<number>
        INFO  : In order to set a constant number of reducers:
        INFO  :   set mapreduce.job.reduces=<number>
        INFO  : number of splits:1
        INFO  : Submitting tokens for job: job_1466104358744_0003
        INFO  : The url to track the job: http://jennykim-1.vpc.cloudera.com:8088/proxy/application_1466104358744_0003/
    """

    assert_equal(self.api.progress({}, snippet, logs=logs), 5)

    logs += """INFO  : Starting Job = job_1466104358744_0003, Tracking URL = http://jennykim-1.vpc.cloudera.com:8088/proxy/application_1466104358744_0003/
        INFO  : Kill Command = /usr/lib/hadoop/bin/hadoop job  -kill job_1466104358744_0003
        INFO  : Hadoop job information for Stage-1: number of mappers: 1; number of reducers: 1
        INFO  : 2016-06-20 13:30:34,494 Stage-1 map = 0%,  reduce = 0%
        INFO  : 2016-06-20 13:30:47,081 Stage-1 map = 100%,  reduce = 0%, Cumulative CPU 3.13 sec
        INFO  : 2016-06-20 13:30:58,606 Stage-1 map = 100%,  reduce = 100%, Cumulative CPU 5.59 sec
        INFO  : MapReduce Total cumulative CPU time: 5 seconds 590 msec
        INFO  : Ended Job = job_1466104358744_0003
    """

    assert_equal(self.api.progress({}, snippet, logs=logs), 50)

    snippet = json.loads("""
        {
            "status": "running",
            "database": "default",
            "id": "d70d31ee-a62a-4854-b2b1-b852f6a390f5",
            "result": {
                "type": "table",
                "handle": {
                  "statement_id": 0,
                  "statements_count": 2,
                  "has_more_statements": true
                },
                "id": "ca11fcb1-11a5-f534-8200-050c8e1e57e3"
            },
            "statement": "%(statement)s",
            "type": "impala",
            "properties": {
                "files": [],
                "functions": [],
                "settings": []
            }
        }
      """ % {'statement': "SELECT * FROM sample_07;"}
    )

    logs = "Query 734a81444c85be66:d05f3bb1a6c2d0a5: 0% Complete (1 out of 4693)"

    assert_equal(self.api.progress({}, snippet, logs=logs), 0)

    logs += """Query 734a81444c85be66:d05f3bb1a6c2d0a5: 20% Complete (4 out of 4693)

    Query 734a81444c85be66:d05f3bb1a6c2d0a5: 30% Complete (7 out of 4693)

    Query 734a81444c85be66:d05f3bb1a6c2d0a5: 40% Complete (7 out of 4693)

    Query 734a81444c85be66:d05f3bb1a6c2d0a5: 50% Complete (234 out of 4693)
    """

    assert_equal(self.api.progress({}, snippet, logs=logs), 50)


  def test_get_jobs(self):

    notebook = json.loads("""
      {
        "uuid": "f5d6394d-364f-56e8-6dd3-b1c5a4738c52",
        "id": 1234,
        "sessions": [{"type": "hive", "properties": [], "id": "1234"}],
        "type": "query-hive",
        "name": "Test Hiveserver2 Editor",
        "isSaved": false,
        "parentUuid": null
      }
    """)

    snippet = json.loads("""
        {
            "status": "running",
            "database": "default",
            "id": "d70d31ee-a62a-4854-b2b1-b852f6a390f5",
            "result": {
                "type": "table",
                "handle": {
                  "statement_id": 0,
                  "statements_count": 2,
                  "has_more_statements": true
                },
                "id": "ca11fcb1-11a5-f534-8200-050c8e1e57e3"
            },
            "statement": "%(statement)s",
            "type": "hive",
            "properties": {
                "files": [],
                "functions": [],
                "settings": []
            }
        }
      """ % {'statement': "SELECT * FROM sample_07;"}
                         )

    logs = """INFO  : Compiling command(queryId=hive_20160624155555_c81f8b95-af22-45fd-8e2c-fb012f530f13): SELECT app,
                     AVG(bytes) AS avg_bytes
            FROM web_logs
            GROUP BY  app
            HAVING app IS NOT NULL
            ORDER BY avg_bytes DESC
            INFO  : Semantic Analysis Completed
            INFO  : Returning Hive schema: Schema(fieldSchemas:[FieldSchema(name:app, type:string, comment:null), FieldSchema(name:avg_bytes, type:double, comment:null)], properties:null)
            INFO  : Completed compiling command(queryId=hive_20160624155555_c81f8b95-af22-45fd-8e2c-fb012f530f13); Time taken: 0.073 seconds
            INFO  : Executing command(queryId=hive_20160624155555_c81f8b95-af22-45fd-8e2c-fb012f530f13): SELECT app,
                     AVG(bytes) AS avg_bytes
            FROM web_logs
            GROUP BY  app
            HAVING app IS NOT NULL
            ORDER BY avg_bytes DESC
            INFO  : Query ID = hive_20160624155555_c81f8b95-af22-45fd-8e2c-fb012f530f13
            INFO  : Total jobs = 2
            INFO  : Launching Job 1 out of 2
            INFO  : Starting task [Stage-1:MAPRED] in serial mode
            INFO  : Number of reduce tasks not specified. Estimated from input data size: 1
            INFO  : In order to change the average load for a reducer (in bytes):
            INFO  :   set hive.exec.reducers.bytes.per.reducer=<number>
            INFO  : In order to limit the maximum number of reducers:
            INFO  :   set hive.exec.reducers.max=<number>
            INFO  : In order to set a constant number of reducers:
            INFO  :   set mapreduce.job.reduces=<number>
            INFO  : number of splits:1
            INFO  : Submitting tokens for job: job_1466630204796_0059
            INFO  : The url to track the job: http://jennykim-1.vpc.cloudera.com:8088/proxy/application_1466630204796_0059/
            INFO  : Starting Job = job_1466630204796_0059, Tracking URL = http://jennykim-1.vpc.cloudera.com:8088/proxy/application_1466630204796_0059/
            INFO  : Kill Command = /usr/lib/hadoop/bin/hadoop job  -kill job_1466630204796_0059
    """

    jobs = self.api.get_jobs(notebook, snippet, logs)
    assert_true(isinstance(jobs, list))
    assert_true(len(jobs), 1)
    assert_equal(jobs[0]['name'], 'job_1466630204796_0059')
    assert_equal(jobs[0]['started'], True)
    assert_equal(jobs[0]['finished'], False)
    assert_true('url' in jobs[0])

    logs += """INFO  : Hadoop job information for Stage-1: number of mappers: 1; number of reducers: 1
        INFO  : 2016-06-24 15:55:51,125 Stage-1 map = 0%,  reduce = 0%
        INFO  : 2016-06-24 15:56:00,410 Stage-1 map = 100%,  reduce = 0%, Cumulative CPU 2.12 sec
        INFO  : 2016-06-24 15:56:09,709 Stage-1 map = 100%,  reduce = 100%, Cumulative CPU 4.04 sec
        INFO  : MapReduce Total cumulative CPU time: 4 seconds 40 msec
        INFO  : Ended Job = job_1466630204796_0059
        INFO  : Launching Job 2 out of 2
    """


    jobs = self.api.get_jobs(notebook, snippet, logs)
    assert_true(len(jobs), 1)
    assert_equal(jobs[0]['name'], 'job_1466630204796_0059')
    assert_equal(jobs[0]['started'], True)
    assert_equal(jobs[0]['finished'], True)


  def test_get_current_statement(self):
    snippet = json.loads("""
        {
            "status": "running",
            "database": "default",
            "id": "d70d31ee-a62a-4854-b2b1-b852f6a390f5",
            "result": {
                "type": "table",
                "handle": {
                  "statement_id": 0,
                  "statements_count": 1,
                  "has_more_statements": false
                },
                "id": "ca11fcb1-11a5-f534-8200-050c8e1e57e3"
            },
            "statement": "%(statement)s",
            "type": "hive",
            "properties": {
                "files": [],
                "functions": [],
                "settings": []
            }
        }
      """ % {'statement': u"SELECT 'Привет', '你好';"}
    )

    statement = self.api._get_current_statement(MockDb(), snippet)

    assert_equal('086ecec9a8b89b1b47cce358bdbb343be23b1f8b54ca76bc81927e27', statement['previous_statement_hash'])


  def test_plan_extraction_from_profile(self):
    query_plan = self.api._get_impala_profile_plan(query_id='e147228183f1f0b3:6f086cc600000000', profile=IMPALA_CUSTOMER_QUERY_SAMPLE_PROFILE)

    assert_true(query_plan)
    assert_equal(IMPALA_CUSTOMER_QUERY_SAMPLE_PROFILE_PLAN, query_plan)


def MockDb():
  def close_operation(handle): pass


class TestHiveserver2ApiWithHadoop(BeeswaxSampleProvider):
  integration = True

  @classmethod
  def setup_class(cls):
    super(TestHiveserver2ApiWithHadoop, cls).setup_class(load_data=False)


  def setUp(self):
    self.client.post('/beeswax/install_examples')

    self.user = User.objects.get(username='test')
    add_to_group('test')
    grant_access("test", "test", "notebook")
    grant_access("test", "test", "impala")

    self.db = dbms.get(self.user, get_query_server_config())
    self.cluster.fs.do_as_user('test', self.cluster.fs.create_home_dir, '/user/test')
    self.api = HS2Api(self.user)

    self.statement = 'SELECT description, salary FROM sample_07 WHERE (sample_07.salary > 100000) ORDER BY salary DESC LIMIT 1000'


  def create_query_document(self, owner, query_type='hive', database='default',
                            name='Test Query', description='Test Query', statement='',
                            files=None, functions=None, settings=None):
      """
      Creates and returns a query Document2 object
      :param owner: owner of doc
      :param query_type: hive, impala or spark
      :param database: database name
      :param name: name of document
      :param description: description of document
      :param statement: SQL statement (can be multi-query statement)
      :param files: list of dicts representing files
      :param functions: list of dicts representing functions
      :param settings: list of dicts representing settings
      :return: Document2 object representing query
      """
      if query_type not in ('hive', 'impala', 'spark'):
          raise ValueError("Invalid query_type: %s" % query_type)

      notebook = make_notebook(name=name, description=description, editor_type=query_type, statement=statement,
                               status='ready', database=database, files=files, functions=functions, settings=settings)
      notebook_doc, save_as = _save_notebook(notebook.get_data(), owner)
      return notebook_doc


  def get_snippet(self, notebook, snippet_idx=0):
    data = notebook.get_data()
    snippet = data['snippets'][snippet_idx]

    if 'result' not in snippet:
      snippet['result'] = {}
    if 'handle' not in snippet['result']:
      snippet['result']['handle'] = {}

    return snippet


  def execute_and_wait(self, query_doc, snippet_idx=0, timeout=30.0, wait=1.0):
      notebook = Notebook(document=query_doc)
      snippet = self.get_snippet(notebook, snippet_idx=snippet_idx)

      curr = time.time()
      end = curr + timeout
      status = 'ready'

      response = self.client.post(reverse('notebook:execute'),
                                  {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})
      notebook = Notebook(document=query_doc)
      snippet = self.get_snippet(notebook, snippet_idx=snippet_idx)
      data = json.loads(response.content)
      snippet['result']['handle'] = data['handle']

      while status != 'available' and curr <= end:
        response = self.client.post(reverse('notebook:check_status'),
                                    {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})
        data = json.loads(response.content)
        status = data['query_status']['status']
        snippet['status'] = status
        time.sleep(wait)
        curr = time.time()

      if status != 'available':
        raise Exception('Query failed to complete or return results.')

      return snippet


  def test_query_with_unicode(self):
    statement = "SELECT * FROM sample_07 WHERE code='한';"

    doc = self.create_query_document(owner=self.user, statement=statement)
    notebook = Notebook(document=doc)
    snippet = self.get_snippet(notebook, snippet_idx=0)

    response = self.client.post(reverse('notebook:execute'),
                                {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})
    data = json.loads(response.content)
    assert_equal(0, data['status'], data)

    snippet['result']['handle'] = data['handle']

    response = self.client.post(reverse('notebook:get_logs'),
                                  {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})
    data = json.loads(response.content)
    assert_equal(0, data['status'], data)
    assert_true("SELECT * FROM sample_07 WHERE code='한'" in smart_str(data['logs']))


  def test_get_current_statement(self):
    multi_statement = "SELECT description, salary FROM sample_07 LIMIT 20;\r\nSELECT AVG(salary) FROM sample_07;"

    doc = self.create_query_document(owner=self.user, statement=multi_statement)
    notebook = Notebook(document=doc)
    snippet = self.get_snippet(notebook, snippet_idx=0)

    response = self.client.post(reverse('notebook:execute'),
                                {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})
    data = json.loads(response.content)

    assert_equal(0, data['status'], data)
    assert_equal(0, data['handle']['statement_id'], data)
    assert_equal(2, data['handle']['statements_count'], data)
    assert_equal(True, data['handle']['has_more_statements'], data)
    assert_equal({'row': 0, 'column': 0}, data['handle']['start'], data)
    assert_equal({'row': 0, 'column': 51}, data['handle']['end'], data)

    snippet['result']['handle'] = data['handle']

    response = self.client.post(reverse('notebook:execute'),
                                {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})
    data = json.loads(response.content)

    assert_equal(0, data['status'], data)
    assert_equal(1, data['handle']['statement_id'], data)
    assert_equal(2, data['handle']['statements_count'], data)
    assert_equal(False, data['handle']['has_more_statements'], data)
    assert_equal({'row': 1, 'column': 0}, data['handle']['start'], data)
    assert_equal({'row': 1, 'column': 33}, data['handle']['end'], data)


  def test_explain(self):
    # Hive 2 with Tez set hive.explain.user to true by default, but this test is expecting output when this setting
    # is set to false.
    doc = self.create_query_document(owner=self.user, statement=self.statement)
    notebook = Notebook(document=doc)
    snippet = self.get_snippet(notebook, snippet_idx=0)
    snippet['properties']['settings'].append({"key": "hive.explain.user", "value": "false"})

    response = self.client.post(reverse('notebook:explain'),
                                {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})

    data = json.loads(response.content)

    assert_equal(0, data['status'], data)
    assert_true('STAGE DEPENDENCIES' in data['explanation'], data)
    assert_equal(self.statement, data['statement'], data)


  def test_download(self):
    statement = "SELECT 'hello world';"

    doc = self.create_query_document(owner=self.user, statement=statement)
    notebook = Notebook(document=doc)
    snippet = self.execute_and_wait(doc, snippet_idx=0)

    response = self.client.post(reverse('notebook:download'),
                                {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet), 'format': 'csv'})

    assert_equal(200, response.status_code)
    assert_equal(('Content-Disposition', 'attachment; filename="Test Query.csv"'), response._headers['content-disposition'])


  def test_get_sample(self):
    doc = self.create_query_document(owner=self.user, statement=self.statement)
    notebook = Notebook(document=doc)
    snippet = self.get_snippet(notebook, snippet_idx=0)

    response = self.client.post(reverse('notebook:api_sample_data',
      kwargs={'database': 'default', 'table': 'sample_07'}),
      {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})
    data = json.loads(response.content)

    assert_equal(0, data['status'], data)
    assert_true('headers' in data)
    assert_true('rows' in data)
    assert_true(len(data['rows']) > 0)

    response = self.client.post(reverse('notebook:api_sample_data_column',
      kwargs={'database': 'default', 'table': 'sample_07', 'column': 'code'}),
      {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})
    data = json.loads(response.content)

    assert_equal(0, data['status'], data)
    assert_true('headers' in data)
    assert_equal(['code'], data['headers'])
    assert_true('rows' in data)
    assert_true(len(data['rows']) > 0)


  def test_fetch_result_size_mr(self):
    if not is_live_cluster():  # Mini-cluster does not have JHS
      raise SkipTest

    # Assert that a query with no job will return no rows or size
    statement = "SELECT 'hello world';"

    settings = [
        {
            'key': 'hive.execution.engine',
            'value': 'mr'
        }
    ]
    doc = self.create_query_document(owner=self.user, statement=statement, settings=settings)
    notebook = Notebook(document=doc)
    snippet = self.execute_and_wait(doc, snippet_idx=0)

    response = self.client.post(reverse('notebook:fetch_result_size'),
                                {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})

    data = json.loads(response.content)
    assert_equal(0, data['status'], data)
    assert_true('result' in data)
    assert_true('rows' in data['result'])
    assert_true('size' in data['result'])
    assert_equal(None, data['result']['rows'])
    assert_equal(None, data['result']['size'])

    # Assert that a query with map & reduce task returns rows
    statement = "SELECT DISTINCT code FROM sample_07;"
    doc = self.create_query_document(owner=self.user, statement=statement, settings=settings)
    notebook = Notebook(document=doc)
    snippet = self.execute_and_wait(doc, snippet_idx=0, timeout=60.0, wait=2.0)

    response = self.client.post(reverse('notebook:fetch_result_size'),
                                {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})

    data = json.loads(response.content)
    assert_equal(0, data['status'], data)
    assert_true('result' in data)
    assert_true('rows' in data['result'])
    assert_true('size' in data['result'])
    assert_equal(823, data['result']['rows'])
    assert_true(data['result']['size'] > 0, data['result'])

    # Assert that a query with multiple jobs returns rows
    statement = "SELECT app, COUNT(1) AS count FROM web_logs GROUP BY app ORDER BY count DESC;"
    doc = self.create_query_document(owner=self.user, statement=statement, settings=settings)
    notebook = Notebook(document=doc)
    snippet = self.execute_and_wait(doc, snippet_idx=0, timeout=120.0, wait=2.0)

    response = self.client.post(reverse('notebook:fetch_result_size'),
                                {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})

    data = json.loads(response.content)
    assert_equal(0, data['status'], data)
    assert_true('result' in data)
    assert_true('rows' in data['result'])
    assert_equal(23, data['result']['rows'])
    assert_true(data['result']['size'] > 0, data['result'])


  def test_fetch_result_size_spark(self):
    if not is_live_cluster() or not is_hive_on_spark():
      raise SkipTest

    # TODO: Add session cleanup here so we don't have orphan spark sessions

    # Assert that a query with no job will return no rows or size
    statement = "SELECT 'hello world';"

    settings = [
        {
            'key': 'hive.execution.engine',
            'value': 'spark'
        }
    ]
    doc = self.create_query_document(owner=self.user, statement=statement, settings=settings)
    notebook = Notebook(document=doc)
    snippet = self.execute_and_wait(doc, snippet_idx=0)

    response = self.client.post(reverse('notebook:fetch_result_size'),
                                {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})

    data = json.loads(response.content)
    assert_equal(0, data['status'], data)
    assert_true('result' in data)
    assert_true('rows' in data['result'])
    assert_true('size' in data['result'])
    assert_equal(None, data['result']['rows'])
    assert_equal(None, data['result']['size'])

    # Assert that a query that runs a job will return rows and size
    statement = "SELECT app, COUNT(1) AS count FROM web_logs GROUP BY app ORDER BY count DESC;"
    doc = self.create_query_document(owner=self.user, statement=statement, settings=settings)
    notebook = Notebook(document=doc)
    snippet = self.execute_and_wait(doc, snippet_idx=0, timeout=60.0, wait=2.0)

    response = self.client.post(reverse('notebook:fetch_result_size'),
                                {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})

    data = json.loads(response.content)
    assert_equal(0, data['status'], data)
    assert_true('result' in data)
    assert_true('rows' in data['result'])
    assert_true('size' in data['result'])
    assert_equal(23, data['result']['rows'])
    assert_true(data['result']['size'] > 0)


  def test_fetch_result_size_impala(self):
    if not is_live_cluster():
      raise SkipTest

    # Create session so that session object is saved to DB for server URL lookup
    session = self.api.create_session(lang='impala')

    try:
      # Assert that a query that runs a job will return rows
      statement = "SELECT app, COUNT(1) AS count FROM web_logs GROUP BY app ORDER BY count DESC;"
      doc = self.create_query_document(owner=self.user, query_type='impala', statement=statement)
      notebook = Notebook(document=doc)
      snippet = self.execute_and_wait(doc, snippet_idx=0, timeout=60.0, wait=2.0)

      self.client.post(reverse('notebook:fetch_result_data'),
                       {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet), 'rows': 100, 'startOver': 'false'})

      response = self.client.post(reverse('notebook:fetch_result_size'),
                                  {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})

      data = json.loads(response.content)
      assert_equal(0, data['status'], data)
      assert_true('result' in data)
      assert_true('rows' in data['result'])
      assert_true('size' in data['result'])
      assert_equal(23, data['result']['rows'])
      assert_equal(None, data['result']['size'])

      # Assert that selecting all from partitioned table works
      statement = "SELECT * FROM web_logs;"
      doc = self.create_query_document(owner=self.user, query_type='impala', statement=statement)
      notebook = Notebook(document=doc)
      snippet = self.execute_and_wait(doc, snippet_idx=0, timeout=60.0, wait=5.0)

      self.client.post(reverse('notebook:fetch_result_data'),
                       {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet), 'rows': 100, 'startOver': 'false'})

      response = self.client.post(reverse('notebook:fetch_result_size'),
                                 {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})

      data = json.loads(response.content)
      assert_equal(0, data['status'], data)
      assert_true('result' in data)
      assert_true('rows' in data['result'])
      assert_equal(1000, data['result']['rows'])
    finally:
      self.api.close_session(session)


  def test_fetch_result_abbreviated(self):
    if not is_live_cluster():
      raise SkipTest

    # Create session so that session object is saved to DB for server URL lookup
    session = self.api.create_session(lang='impala')

    try:

      # Assert that abbreviated rows returned (e.g. - 1.00K) still returns actual rows
      statement = "SELECT * FROM web_logs;"
      doc = self.create_query_document(owner=self.user, query_type='impala', statement=statement)
      notebook = Notebook(document=doc)
      snippet = self.execute_and_wait(doc, snippet_idx=0, timeout=60.0, wait=5.0)

      self.client.post(reverse('notebook:fetch_result_data'),
                       {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet), 'rows': 100, 'startOver': 'false'})

      response = self.client.post(reverse('notebook:fetch_result_size'),
                                  {'notebook': notebook.get_json(), 'snippet': json.dumps(snippet)})

      data = json.loads(response.content)
      assert_equal(0, data['status'], data)
      assert_true('result' in data)
      assert_true('rows' in data['result'])
      assert_equal(1000, data['result']['rows'])
    finally:
      self.api.close_session(session)


IMPALA_CUSTOMER_QUERY_SAMPLE_PROFILE_PLAN = """Query (id=e147228183f1f0b3:6f086cc600000000):
  Summary:
    Session ID: 4043f7580371e0e6:f1068bf772ce4cb3
    Session Type: HIVESERVER2
    HiveServer2 Protocol Version: V6
    Start Time: 2017-10-13 10:47:09.373244000
    End Time: 2017-10-13 10:50:08.731647000
    Query Type: QUERY
    Query State: FINISHED
    Query Status: OK
    Impala Version: impalad version 2.11.0-SNAPSHOT RELEASE (build e9a30f67655a8da5b8526507fbe853adbd184932)
    User: romain
    Connected User: romain
    Delegated User:
    Network Address: 172.21.3.229:60523
    Default Db: default
    Sql Statement:



-- Compute total amount per order for all customers
SELECT
  c.id AS customer_id,
 c.name AS customer_name,
  o.order_id,
  v.total
FROM
  customers c,
  c.orders o,
  (SELECT SUM(price * qty) total FROM o.items) v
    Coordinator: self-service-analytics-2.gce.cloudera.com:22000
    Query Options (set by configuration): QUERY_TIMEOUT_S=600
    Query Options (set by configuration and planner): QUERY_TIMEOUT_S=600,MT_DOP=0
    Plan:
----------------
Max Per-Host Resource Reservation: Memory=0B
Per-Host Resource Estimates: Memory=42.00MB
WARNING: The following tables have potentially corrupt table statistics.
Drop and re-compute statistics to resolve this problem.
default.customers
WARNING: The following tables are missing relevant table and/or column statistics.
default.customers

F01:PLAN FRAGMENT [UNPARTITIONED] hosts=1 instances=1
|  Per-Host Resources: mem-estimate=0B mem-reservation=0B
PLAN-ROOT SINK
|  mem-estimate=0B mem-reservation=0B
|
10:EXCHANGE [UNPARTITIONED]
|  mem-estimate=0B mem-reservation=0B
|  tuple-ids=3,1,0 row-size=75B cardinality=0
|
F00:PLAN FRAGMENT [RANDOM] hosts=1 instances=1
Per-Host Resources: mem-estimate=42.00MB mem-reservation=0B
01:SUBPLAN
|  mem-estimate=0B mem-reservation=0B
|  tuple-ids=3,1,0 row-size=75B cardinality=0
|
|--09:NESTED LOOP JOIN [CROSS JOIN]
|  |  mem-estimate=35B mem-reservation=0B
|  |  tuple-ids=3,1,0 row-size=75B cardinality=10
|  |
|  |--02:SINGULAR ROW SRC
|  |     parent-subplan=01
|  |     mem-estimate=0B mem-reservation=0B
|  |     tuple-ids=0 row-size=35B cardinality=1
|  |
|  04:SUBPLAN
|  |  mem-estimate=0B mem-reservation=0B
|  |  tuple-ids=3,1 row-size=40B cardinality=10
|  |
|  |--08:NESTED LOOP JOIN [CROSS JOIN]
|  |  |  mem-estimate=32B mem-reservation=0B
|  |  |  tuple-ids=3,1 row-size=40B cardinality=1
|  |  |
|  |  |--05:SINGULAR ROW SRC
|  |  |     parent-subplan=04
|  |  |     mem-estimate=0B mem-reservation=0B
|  |  |     tuple-ids=1 row-size=32B cardinality=1
|  |  |
|  |  07:AGGREGATE [FINALIZE]
|  |  |  output: sum(price * qty)
|  |  |  mem-estimate=10.00MB mem-reservation=0B spill-buffer=2.00MB
|  |  |  tuple-ids=3 row-size=8B cardinality=1
|  |  |
|  |  06:UNNEST [o.items]
|  |     parent-subplan=04
|  |     mem-estimate=0B mem-reservation=0B
|  |     tuple-ids=2 row-size=0B cardinality=10
|  |
|  03:UNNEST [c.orders o]
|     parent-subplan=01
|     mem-estimate=0B mem-reservation=0B
|     tuple-ids=1 row-size=0B cardinality=10
|
00:SCAN HDFS [default.customers c, RANDOM]
   partitions=1/1 files=1 size=15.44KB
   predicates: !empty(c.orders)
   stats-rows=0 extrapolated-rows=disabled
   table stats: rows=0 size=15.44KB
   column stats: unavailable
   mem-estimate=32.00MB mem-reservation=0B
   tuple-ids=0 row-size=35B cardinality=0
----------------
    Estimated Per-Host Mem: 44040259
    Tables Missing Stats: default.customers
    Tables With Corrupt Table Stats: default.customers
    Per Host Min Reservation: self-service-analytics-2.gce.cloudera.com:22000(0)
    Request Pool: root.romain
    Admission result: Admitted immediately
    ExecSummary:
Operator                       #Hosts  Avg Time  Max Time  #Rows  Est. #Rows   Peak Mem  Est. Peak Mem  Detail
----------------------------------------------------------------------------------------------------------------------------
10:EXCHANGE                         1  62.005ms  62.005ms    106           0          0              0  UNPARTITIONED
01:SUBPLAN                          1   0.000ns   0.000ns      0           0  140.00 KB              0
|--09:NESTED LOOP JOIN              1   0.000ns   0.000ns  5.67K          10   32.00 KB        35.00 B  CROSS JOIN
|  |--02:SINGULAR ROW SRC           1   0.000ns   0.000ns      0           1          0              0
|  04:SUBPLAN                       1   0.000ns   0.000ns      0          10    8.00 KB              0
|  |--08:NESTED LOOP JOIN           1   0.000ns   0.000ns    160           1   24.00 KB        32.00 B  CROSS JOIN
|  |  |--05:SINGULAR ROW SRC        1   0.000ns   0.000ns      0           1          0              0
|  |  07:AGGREGATE                  1   0.000ns   0.000ns      1           1   16.00 KB       10.00 MB  FINALIZE
|  |  06:UNNEST                     1   0.000ns   0.000ns      2          10          0              0  o.items
|  03:UNNEST                        1   0.000ns   0.000ns      2          10          0              0  c.orders o
00:SCAN HDFS                        1  39.003ms  39.003ms     53           0  417.04 KB       32.00 MB  default.customers c
    Errors:
    Planner Timeline: 36.379ms
       - Analysis finished: 13.156ms (13.156ms)
       - Equivalence classes computed: 13.775ms (619.949us)
       - Single node plan created: 20.763ms (6.987ms)
       - Runtime filters computed: 21.325ms (562.117us)
       - Distributed plan created: 21.460ms (135.254us)
       - Lineage info computed: 21.684ms (223.594us)
       - Planning finished: 36.379ms (14.694ms)
    Query Timeline: 2m59s
       - Query submitted: 0.000ns (0.000ns)
       - Planning finished: 42.003ms (42.003ms)
       - Submit for admission: 43.003ms (1.000ms)
       - Completed admission: 43.003ms (0.000ns)
       - Ready to start on 1 backends: 43.003ms (0.000ns)
       - All 1 execution backends (2 fragment instances) started: 44.003ms (1.000ms)
       - Rows available: 121.009ms (77.006ms)
       - First row fetched: 1s152ms (1s031ms)
       - Unregister query: 2m59s (2m58s)
     - ComputeScanRangeAssignmentTimer: 0.000ns
  ImpalaServer:
     - ClientFetchWaitTimer: 2m59s
     - RowMaterializationTimer: 1.000ms
  Execution Profile e147228183f1f0b3:6f086cc600000000"""

IMPALA_CUSTOMER_QUERY_SAMPLE_PROFILE = IMPALA_CUSTOMER_QUERY_SAMPLE_PROFILE_PLAN + \
  """:(Total: 79.006ms, non-child: 0.000ns, % non-child: 0.00%)
    Number of filters: 0
    Filter routing table:
 ID  Src. Node  Tgt. Node(s)  Target type  Partition filter  Pending (Expected)  First arrived  Completed   Enabled
-------------------------------------------------------------------------------------------------------------------

    Backend startup latencies: Count: 1, min / max: 1ms / 1ms, 25th %-ile: 1ms, 50th %-ile: 1ms, 75th %-ile: 1ms, 90th %-ile: 1ms, 95th %-ile: 1ms, 99.9th %-ile: 1ms
    Per Node Peak Memory Usage: self-service-analytics-2.gce.cloudera.com:22000(530.52 KB)
     - FiltersReceived: 0 (0)
     - FinalizationTimer: 0.000ns
    Averaged Fragment F01:(Total: 76.006ms, non-child: 1.000ms, % non-child: 1.32%)
      split sizes:  min: 0, max: 0, avg: 0, stddev: 0
      completion times: min:2m59s  max:2m59s  mean: 2m59s  stddev:0.000ns
      execution rates: min:0.00 /sec  max:0.00 /sec  mean:0.00 /sec  stddev:0.00 /sec
      num instances: 1
       - AverageThreadTokens: 0.00
       - BloomFilterBytes: 0
       - PeakMemoryUsage: 34.12 KB (34939)
       - PeakReservation: 0
       - PeakUsedReservation: 0
       - PerHostPeakMemUsage: 530.52 KB (543253)
       - RowsProduced: 106 (106)
       - TotalNetworkReceiveTime: 62.005ms
       - TotalNetworkSendTime: 0.000ns
       - TotalStorageWaitTime: 0.000ns
       - TotalThreadsInvoluntaryContextSwitches: 0 (0)
       - TotalThreadsTotalWallClockTime: 62.005ms
         - TotalThreadsSysTime: 3.000us
         - TotalThreadsUserTime: 12.000us
       - TotalThreadsVoluntaryContextSwitches: 1 (1)
      Fragment Instance Lifecycle Timings:
         - ExecTime: 0.000ns
           - ExecTreeExecTime: 0.000ns
         - OpenTime: 62.005ms
           - ExecTreeOpenTime: 62.005ms
         - PrepareTime: 14.001ms
           - ExecTreePrepareTime: 0.000ns
      PLAN_ROOT_SINK:
         - PeakMemoryUsage: 0
      CodeGen:(Total: 13.001ms, non-child: 13.001ms, % non-child: 100.00%)
         - CodegenTime: 0.000ns
         - CompileTime: 0.000ns
         - LoadTime: 0.000ns
         - ModuleBitcodeSize: 1.84 MB (1929624)
         - NumFunctions: 0 (0)
         - NumInstructions: 0 (0)
         - OptimizationTime: 0.000ns
         - PeakMemoryUsage: 0
         - PrepareTime: 13.001ms
      EXCHANGE_NODE (id=10):(Total: 62.005ms, non-child: 62.005ms, % non-child: 100.00%)
         - ConvertRowBatchTime: 0.000ns
         - PeakMemoryUsage: 0
         - RowsReturned: 106 (106)
         - RowsReturnedRate: 1.71 K/sec
        DataStreamReceiver:
           - BytesReceived: 5.50 KB (5632)
           - DeserializeRowBatchTimer: 0.000ns
           - FirstBatchArrivalWaitTime: 62.005ms
           - PeakMemoryUsage: 10.12 KB (10363)
           - SendersBlockedTimer: 0.000ns
           - SendersBlockedTotalTimer(*): 0.000ns
    Coordinator Fragment F01:
      Instance e147228183f1f0b3:6f086cc600000000 (host=self-service-analytics-2.gce.cloudera.com:22000):(Total: 76.006ms, non-child: 1.000ms, % non-child: 1.32%)
        MemoryUsage(4s000ms): 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB, 31.64 KB
         - AverageThreadTokens: 0.00
         - BloomFilterBytes: 0
         - PeakMemoryUsage: 34.12 KB (34939)
         - PeakReservation: 0
         - PeakUsedReservation: 0
         - PerHostPeakMemUsage: 530.52 KB (543253)
         - RowsProduced: 106 (106)
         - TotalNetworkReceiveTime: 62.005ms
         - TotalNetworkSendTime: 0.000ns
         - TotalStorageWaitTime: 0.000ns
         - TotalThreadsInvoluntaryContextSwitches: 0 (0)
         - TotalThreadsTotalWallClockTime: 62.005ms
           - TotalThreadsSysTime: 3.000us
           - TotalThreadsUserTime: 12.000us
         - TotalThreadsVoluntaryContextSwitches: 1 (1)
        Fragment Instance Lifecycle Timings:
           - ExecTime: 0.000ns
             - ExecTreeExecTime: 0.000ns
           - OpenTime: 62.005ms
             - ExecTreeOpenTime: 62.005ms
           - PrepareTime: 14.001ms
             - ExecTreePrepareTime: 0.000ns
        PLAN_ROOT_SINK:
           - PeakMemoryUsage: 0
        CodeGen:(Total: 13.001ms, non-child: 13.001ms, % non-child: 100.00%)
           - CodegenTime: 0.000ns
           - CompileTime: 0.000ns
           - LoadTime: 0.000ns
           - ModuleBitcodeSize: 1.84 MB (1929624)
           - NumFunctions: 0 (0)
           - NumInstructions: 0 (0)
           - OptimizationTime: 0.000ns
           - PeakMemoryUsage: 0
           - PrepareTime: 13.001ms
        EXCHANGE_NODE (id=10):(Total: 62.005ms, non-child: 62.005ms, % non-child: 100.00%)
           - ConvertRowBatchTime: 0.000ns
           - PeakMemoryUsage: 0
           - RowsReturned: 106 (106)
           - RowsReturnedRate: 1.71 K/sec
          DataStreamReceiver:
            BytesReceived(4s000ms): 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB, 5.50 KB
             - BytesReceived: 5.50 KB (5632)
             - DeserializeRowBatchTimer: 0.000ns
             - FirstBatchArrivalWaitTime: 62.005ms
             - PeakMemoryUsage: 10.12 KB (10363)
             - SendersBlockedTimer: 0.000ns
             - SendersBlockedTotalTimer(*): 0.000ns
    Averaged Fragment F00:(Total: 76.006ms, non-child: 1.000ms, % non-child: 1.32%)
      split sizes:  min: 15.44 KB, max: 15.44 KB, avg: 15.44 KB, stddev: 0
      completion times: min:78.006ms  max:78.006ms  mean: 78.006ms  stddev:0.000ns
      execution rates: min:197.95 KB/sec  max:197.95 KB/sec  mean:197.95 KB/sec  stddev:0.00 /sec
      num instances: 1
       - AverageThreadTokens: 0.00
       - BloomFilterBytes: 0
       - PeakMemoryUsage: 506.52 KB (518677)
       - PeakReservation: 0
       - PeakUsedReservation: 0
       - PerHostPeakMemUsage: 530.52 KB (543253)
       - RowsProduced: 106 (106)
       - TotalNetworkReceiveTime: 0.000ns
       - TotalNetworkSendTime: 0.000ns
       - TotalStorageWaitTime: 38.003ms
       - TotalThreadsInvoluntaryContextSwitches: 1 (1)
       - TotalThreadsTotalWallClockTime: 100.008ms
         - TotalThreadsSysTime: 1.520ms
         - TotalThreadsUserTime: 22.153ms
       - TotalThreadsVoluntaryContextSwitches: 8 (8)
      Fragment Instance Lifecycle Timings:
         - ExecTime: 39.003ms
           - ExecTreeExecTime: 39.003ms
         - OpenTime: 22.001ms
           - ExecTreeOpenTime: 0.000ns
         - PrepareTime: 15.001ms
           - ExecTreePrepareTime: 0.000ns
      DataStreamSender (dst_id=10):
         - BytesSent: 5.50 KB (5632)
         - NetworkThroughput(*): 0.00 /sec
         - OverallThroughput: 0.00 /sec
         - PeakMemoryUsage: 4.85 KB (4968)
         - RowsReturned: 106 (106)
         - SerializeBatchTime: 0.000ns
         - TransmitDataRPCTime: 0.000ns
         - UncompressedRowBatchSize: 8.89 KB (9103)
      CodeGen:(Total: 36.002ms, non-child: 36.002ms, % non-child: 100.00%)
         - CodegenTime: 2.000ms
         - CompileTime: 7.000ms
         - LoadTime: 0.000ns
         - ModuleBitcodeSize: 1.84 MB (1929624)
         - NumFunctions: 23 (23)
         - NumInstructions: 365 (365)
         - OptimizationTime: 15.001ms
         - PeakMemoryUsage: 182.50 KB (186880)
         - PrepareTime: 14.001ms
      SUBPLAN_NODE (id=1):(Total: 39.003ms, non-child: 0.000ns, % non-child: 0.00%)
         - PeakMemoryUsage: 140.00 KB (143360)
         - RowsReturned: 0 (0)
         - RowsReturnedRate: 0
        NESTED_LOOP_JOIN_NODE (id=9):
           - BuildRows: 0 (0)
           - BuildTime: 0.000ns
           - PeakMemoryUsage: 32.00 KB (32768)
           - ProbeRows: 106 (106)
           - ProbeTime: 0.000ns
           - RowsReturned: 5.67K (5671)
           - RowsReturnedRate: 0
          Nested Loop Join Builder:
             - PeakMemoryUsage: 8.00 KB (8192)
          SINGULAR_ROW_SRC_NODE (id=2):
             - PeakMemoryUsage: 0
             - RowsReturned: 0 (0)
             - RowsReturnedRate: 0
        SUBPLAN_NODE (id=4):
           - PeakMemoryUsage: 8.00 KB (8192)
           - RowsReturned: 0 (0)
           - RowsReturnedRate: 0
          NESTED_LOOP_JOIN_NODE (id=8):
             - BuildRows: 0 (0)
             - BuildTime: 0.000ns
             - PeakMemoryUsage: 24.00 KB (24576)
             - ProbeRows: 106 (106)
             - ProbeTime: 0.000ns
             - RowsReturned: 160 (160)
             - RowsReturnedRate: 0
            Nested Loop Join Builder:
               - PeakMemoryUsage: 8.00 KB (8192)
            SINGULAR_ROW_SRC_NODE (id=5):
               - PeakMemoryUsage: 0
               - RowsReturned: 0 (0)
               - RowsReturnedRate: 0
          AGGREGATION_NODE (id=7):
             - BuildTime: 0.000ns
             - GetResultsTime: 0.000ns
             - HTResizeTime: 0.000ns
             - HashBuckets: 0 (0)
             - LargestPartitionPercent: 0 (0)
             - MaxPartitionLevel: 0 (0)
             - NumRepartitions: 0 (0)
             - PartitionsCreated: 0 (0)
             - PeakMemoryUsage: 16.00 KB (16384)
             - RowsRepartitioned: 0 (0)
             - RowsReturned: 1 (1)
             - RowsReturnedRate: 0
             - SpilledPartitions: 0 (0)
          UNNEST_NODE (id=6):
             - AvgCollectionSize: 1.50
             - MaxCollectionSize: 3 (3)
             - MinCollectionSize: 1 (1)
             - NumCollections: 106 (106)
             - PeakMemoryUsage: 0
             - RowsReturned: 2 (2)
             - RowsReturnedRate: 0
        UNNEST_NODE (id=3):
           - AvgCollectionSize: 2.00
           - MaxCollectionSize: 3 (3)
           - MinCollectionSize: 1 (1)
           - NumCollections: 53 (53)
           - PeakMemoryUsage: 0
           - RowsReturned: 2 (2)
           - RowsReturnedRate: 0
      HDFS_SCAN_NODE (id=0):(Total: 39.003ms, non-child: 39.003ms, % non-child: 100.00%)
         - AverageHdfsReadThreadConcurrency: 0.00
         - AverageScannerThreadConcurrency: 0.00
         - BytesRead: 19.30 KB (19766)
         - BytesReadDataNodeCache: 0
         - BytesReadLocal: 19.30 KB (19766)
         - BytesReadRemoteUnexpected: 0
         - BytesReadShortCircuit: 19.30 KB (19766)
         - CachedFileHandlesHitCount: 5 (5)
         - CachedFileHandlesMissCount: 1 (1)
         - CollectionItemsRead: 265 (265)
         - DecompressionTime: 0.000ns
         - MaxCompressedTextFileLength: 0
         - NumColumns: 5 (5)
         - NumDictFilteredRowGroups: 0 (0)
         - NumDisksAccessed: 1 (1)
         - NumRowGroups: 1 (1)
         - NumScannerThreadsStarted: 1 (1)
         - NumScannersWithNoReads: 0 (0)
         - NumStatsFilteredRowGroups: 0 (0)
         - PeakMemoryUsage: 417.04 KB (427045)
         - PerReadThreadRawHdfsThroughput: 507.92 KB/sec
         - RemoteScanRanges: 0 (0)
         - RowBatchQueueGetWaitTime: 39.003ms
         - RowBatchQueuePutWaitTime: 0.000ns
         - RowsRead: 53 (53)
         - RowsReturned: 53 (53)
         - RowsReturnedRate: 1.36 K/sec
         - ScanRangesComplete: 1 (1)
         - ScannerThreadsInvoluntaryContextSwitches: 0 (0)
         - ScannerThreadsTotalWallClockTime: 39.003ms
           - MaterializeTupleTime(*): 1.000ms
           - ScannerThreadsSysTime: 346.000us
           - ScannerThreadsUserTime: 346.000us
         - ScannerThreadsVoluntaryContextSwitches: 4 (4)
         - TotalRawHdfsReadTime(*): 38.003ms
         - TotalReadThroughput: 0.00 /sec
    Fragment F00:
      Instance e147228183f1f0b3:6f086cc600000001 (host=self-service-analytics-2.gce.cloudera.com:22000):(Total: 76.006ms, non-child: 1.000ms, % non-child: 1.32%)
        Hdfs split stats (<volume id>:<# splits>/<split lengths>): 0:1/15.44 KB
         - AverageThreadTokens: 0.00
         - BloomFilterBytes: 0
         - PeakMemoryUsage: 506.52 KB (518677)
         - PeakReservation: 0
         - PeakUsedReservation: 0
         - PerHostPeakMemUsage: 530.52 KB (543253)
         - RowsProduced: 106 (106)
         - TotalNetworkReceiveTime: 0.000ns
         - TotalNetworkSendTime: 0.000ns
         - TotalStorageWaitTime: 38.003ms
         - TotalThreadsInvoluntaryContextSwitches: 1 (1)
         - TotalThreadsTotalWallClockTime: 100.008ms
           - TotalThreadsSysTime: 1.520ms
           - TotalThreadsUserTime: 22.153ms
         - TotalThreadsVoluntaryContextSwitches: 8 (8)
        Fragment Instance Lifecycle Timings:
           - ExecTime: 39.003ms
             - ExecTreeExecTime: 39.003ms
           - OpenTime: 22.001ms
             - ExecTreeOpenTime: 0.000ns
           - PrepareTime: 15.001ms
             - ExecTreePrepareTime: 0.000ns
        DataStreamSender (dst_id=10):
           - BytesSent: 5.50 KB (5632)
           - NetworkThroughput(*): 0.00 /sec
           - OverallThroughput: 0.00 /sec
           - PeakMemoryUsage: 4.85 KB (4968)
           - RowsReturned: 106 (106)
           - SerializeBatchTime: 0.000ns
           - TransmitDataRPCTime: 0.000ns
           - UncompressedRowBatchSize: 8.89 KB (9103)
        CodeGen:(Total: 36.002ms, non-child: 36.002ms, % non-child: 100.00%)
           - CodegenTime: 2.000ms
           - CompileTime: 7.000ms
           - LoadTime: 0.000ns
           - ModuleBitcodeSize: 1.84 MB (1929624)
           - NumFunctions: 23 (23)
           - NumInstructions: 365 (365)
           - OptimizationTime: 15.001ms
           - PeakMemoryUsage: 182.50 KB (186880)
           - PrepareTime: 14.001ms
        SUBPLAN_NODE (id=1):(Total: 39.003ms, non-child: 0.000ns, % non-child: 0.00%)
           - PeakMemoryUsage: 140.00 KB (143360)
           - RowsReturned: 0 (0)
           - RowsReturnedRate: 0
          NESTED_LOOP_JOIN_NODE (id=9):
             - BuildRows: 0 (0)
             - BuildTime: 0.000ns
             - PeakMemoryUsage: 32.00 KB (32768)
             - ProbeRows: 106 (106)
             - ProbeTime: 0.000ns
             - RowsReturned: 5.67K (5671)
             - RowsReturnedRate: 0
            Nested Loop Join Builder:
               - PeakMemoryUsage: 8.00 KB (8192)
            SINGULAR_ROW_SRC_NODE (id=2):
               - PeakMemoryUsage: 0
               - RowsReturned: 0 (0)
               - RowsReturnedRate: 0
          SUBPLAN_NODE (id=4):
             - PeakMemoryUsage: 8.00 KB (8192)
             - RowsReturned: 0 (0)
             - RowsReturnedRate: 0
            NESTED_LOOP_JOIN_NODE (id=8):
               - BuildRows: 0 (0)
               - BuildTime: 0.000ns
               - PeakMemoryUsage: 24.00 KB (24576)
               - ProbeRows: 106 (106)
               - ProbeTime: 0.000ns
               - RowsReturned: 160 (160)
               - RowsReturnedRate: 0
              Nested Loop Join Builder:
                 - PeakMemoryUsage: 8.00 KB (8192)
              SINGULAR_ROW_SRC_NODE (id=5):
                 - PeakMemoryUsage: 0
                 - RowsReturned: 0 (0)
                 - RowsReturnedRate: 0
            AGGREGATION_NODE (id=7):
              ExecOption: Codegen Enabled
               - BuildTime: 0.000ns
               - GetResultsTime: 0.000ns
               - HTResizeTime: 0.000ns
               - HashBuckets: 0 (0)
               - LargestPartitionPercent: 0 (0)
               - MaxPartitionLevel: 0 (0)
               - NumRepartitions: 0 (0)
               - PartitionsCreated: 0 (0)
               - PeakMemoryUsage: 16.00 KB (16384)
               - RowsRepartitioned: 0 (0)
               - RowsReturned: 1 (1)
               - RowsReturnedRate: 0
               - SpilledPartitions: 0 (0)
            UNNEST_NODE (id=6):
               - AvgCollectionSize: 1.50
               - MaxCollectionSize: 3 (3)
               - MinCollectionSize: 1 (1)
               - NumCollections: 106 (106)
               - PeakMemoryUsage: 0
               - RowsReturned: 2 (2)
               - RowsReturnedRate: 0
          UNNEST_NODE (id=3):
             - AvgCollectionSize: 2.00
             - MaxCollectionSize: 3 (3)
             - MinCollectionSize: 1 (1)
             - NumCollections: 53 (53)
             - PeakMemoryUsage: 0
             - RowsReturned: 2 (2)
             - RowsReturnedRate: 0
        HDFS_SCAN_NODE (id=0):(Total: 39.003ms, non-child: 39.003ms, % non-child: 100.00%)
          Hdfs split stats (<volume id>:<# splits>/<split lengths>): 0:1/15.44 KB
          ExecOption: PARQUET Codegen Enabled, Codegen enabled: 1 out of 1
          Hdfs Read Thread Concurrency Bucket: 0:0% 1:0% 2:0% 3:0% 4:0%
          File Formats: PARQUET/NONE:5
           - FooterProcessingTime: (Avg: 38.003ms ; Min: 38.003ms ; Max: 38.003ms ; Number of samples: 1)
           - AverageHdfsReadThreadConcurrency: 0.00
           - AverageScannerThreadConcurrency: 0.00
           - BytesRead: 19.30 KB (19766)
           - BytesReadDataNodeCache: 0
           - BytesReadLocal: 19.30 KB (19766)
           - BytesReadRemoteUnexpected: 0
           - BytesReadShortCircuit: 19.30 KB (19766)
           - CachedFileHandlesHitCount: 5 (5)
           - CachedFileHandlesMissCount: 1 (1)
           - CollectionItemsRead: 265 (265)
           - DecompressionTime: 0.000ns
           - MaxCompressedTextFileLength: 0
           - NumColumns: 5 (5)
           - NumDictFilteredRowGroups: 0 (0)
           - NumDisksAccessed: 1 (1)
           - NumRowGroups: 1 (1)
           - NumScannerThreadsStarted: 1 (1)
           - NumScannersWithNoReads: 0 (0)
           - NumStatsFilteredRowGroups: 0 (0)
           - PeakMemoryUsage: 417.04 KB (427045)
           - PerReadThreadRawHdfsThroughput: 507.92 KB/sec
           - RemoteScanRanges: 0 (0)
           - RowBatchQueueGetWaitTime: 39.003ms
           - RowBatchQueuePutWaitTime: 0.000ns
           - RowsRead: 53 (53)
           - RowsReturned: 53 (53)
           - RowsReturnedRate: 1.36 K/sec
           - ScanRangesComplete: 1 (1)
           - ScannerThreadsInvoluntaryContextSwitches: 0 (0)
           - ScannerThreadsTotalWallClockTime: 39.003ms
             - MaterializeTupleTime(*): 1.000ms
             - ScannerThreadsSysTime: 346.000us
             - ScannerThreadsUserTime: 346.000us
           - ScannerThreadsVoluntaryContextSwitches: 4 (4)
           - TotalRawHdfsReadTime(*): 38.003ms
           - TotalReadThroughput: 0.00 /sec
"""
