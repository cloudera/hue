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
from django.core.urlresolvers import reverse

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

    assert_equal(self.api.progress(snippet, logs), 5)

    logs += """INFO  : Starting Job = job_1466104358744_0003, Tracking URL = http://jennykim-1.vpc.cloudera.com:8088/proxy/application_1466104358744_0003/
        INFO  : Kill Command = /usr/lib/hadoop/bin/hadoop job  -kill job_1466104358744_0003
        INFO  : Hadoop job information for Stage-1: number of mappers: 1; number of reducers: 1
        INFO  : 2016-06-20 13:30:34,494 Stage-1 map = 0%,  reduce = 0%
        INFO  : 2016-06-20 13:30:47,081 Stage-1 map = 100%,  reduce = 0%, Cumulative CPU 3.13 sec
        INFO  : 2016-06-20 13:30:58,606 Stage-1 map = 100%,  reduce = 100%, Cumulative CPU 5.59 sec
        INFO  : MapReduce Total cumulative CPU time: 5 seconds 590 msec
        INFO  : Ended Job = job_1466104358744_0003
    """

    assert_equal(self.api.progress(snippet, logs), 50)

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

    assert_equal(self.api.progress(snippet, logs), 0)

    logs += """Query 734a81444c85be66:d05f3bb1a6c2d0a5: 20% Complete (4 out of 4693)

    Query 734a81444c85be66:d05f3bb1a6c2d0a5: 30% Complete (7 out of 4693)

    Query 734a81444c85be66:d05f3bb1a6c2d0a5: 40% Complete (7 out of 4693)

    Query 734a81444c85be66:d05f3bb1a6c2d0a5: 50% Complete (234 out of 4693)
    """

    assert_equal(self.api.progress(snippet, logs), 50)


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


def MockDb():
  def close_operation(handle): pass


class TestHiveserver2ApiWithHadoop(BeeswaxSampleProvider):

  @classmethod
  def setup_class(cls):
    super(TestHiveserver2ApiWithHadoop, cls).setup_class(load_data=False)


  def setUp(self):
    self.client.post('/beeswax/install_examples')

    self.user = User.objects.get(username='test')
    add_to_group('test')
    grant_access("test", "test", "notebook")

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
    assert_equal(('Content-Disposition', 'attachment; filename=Test Query.csv'), response._headers['content-disposition'])


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
    snippet = self.execute_and_wait(doc, snippet_idx=0, timeout=60.0, wait=2.0)

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
