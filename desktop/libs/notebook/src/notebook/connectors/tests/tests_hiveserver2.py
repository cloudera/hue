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

from nose.tools import assert_equal, assert_true, assert_false

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import add_to_group, grant_access
from desktop.models import Document2
from notebook.connectors.hiveserver2 import HS2Api

from beeswax.server import dbms
from beeswax.test_base import BeeswaxSampleProvider, get_query_server_config


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


class TestHiveserver2ApiWithHadoop(BeeswaxSampleProvider):

  @classmethod
  def setup_class(cls):
    super(TestHiveserver2ApiWithHadoop, cls).setup_class(load_data=False)


  def setUp(self):
    self.client.post('/beeswax/install_examples')

    self.user = User.objects.get(username='test')
    grant_access("test", "test", "notebook")

    self.db = dbms.get(self.user, get_query_server_config())
    self.cluster.fs.do_as_user('test', self.cluster.fs.create_home_dir, '/user/test')
    self.api = HS2Api(self.user)

    self.notebook_json = """
      {
        "uuid": "f5d6394d-364f-56e8-6dd3-b1c5a4738c52",
        "id": 1234,
        "sessions": [{"type": "hive", "properties": [], "id": "1234"}],
        "type": "query-hive",
        "name": "Test Hiveserver2 Editor",
        "isSaved": false,
        "parentUuid": null
      }
    """
    self.statement = 'SELECT description, salary FROM sample_07 WHERE (sample_07.salary > 100000) ORDER BY salary DESC LIMIT 1000'
    self.snippet_json = """
      {
          "status": "running",
          "database": "%(database)s",
          "id": "d70d31ee-a62a-4854-b2b1-b852f6a390f5",
          "result": {
              "type": "table",
              "handle": {},
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
    """ % {'database': self.db_name, 'statement': self.statement}

    doc, created = Document2.objects.get_or_create(
      id=1234,
      name='Test Hive Query',
      type='query-hive',
      owner=self.user,
      is_history=True,
      data=self.notebook_json)


  def test_query_with_unicode(self):
    statement = "SELECT * FROM sample_07 WHERE code='validé';"

    snippet_json = json.loads("""
        {
            "status": "running",
            "database": "default",
            "id": "d70d31ee-a62a-4854-b2b1-b852f6a390f5",
            "result": {
                "type": "table",
                "handle": {},
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
      """ % {'statement': statement})

    notebook_json = json.loads(self.notebook_json)
    notebook_json['snippets'] = [snippet_json]
    response = self.client.post(reverse('notebook:execute'),
                                {'notebook': json.dumps(notebook_json), 'snippet': json.dumps(snippet_json)})
    data = json.loads(response.content)
    assert_equal(0, data['status'], data)


  def test_get_current_statement(self):
    multi_statement = "SELECT description, salary FROM sample_07 LIMIT 20;\\r\\nSELECT AVG(salary) FROM sample_07;"
    snippet_json = json.loads("""
      {
          "status": "running",
          "database": "default",
          "id": "d70d31ee-a62a-4854-b2b1-b852f6a390f5",
          "result": {
              "type": "table",
              "handle": {},
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
    """ % {'statement': multi_statement}
    )

    notebook_json = json.loads(self.notebook_json)
    notebook_json['snippets'] = [snippet_json]
    response = self.client.post(reverse('notebook:execute'), {'notebook': json.dumps(notebook_json), 'snippet': json.dumps(snippet_json)})
    data = json.loads(response.content)

    assert_equal(0, data['status'], data)
    assert_equal(0, data['handle']['statement_id'], data)
    assert_equal(2, data['handle']['statements_count'], data)
    assert_equal(True, data['handle']['has_more_statements'], data)
    assert_equal({'row': 0, 'column': 0}, data['handle']['start'], data)
    assert_equal({'row': 0, 'column': 51}, data['handle']['end'], data)


    snippet_json = json.loads("""
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
    """ % {'statement': multi_statement}
    )

    notebook_json = json.loads(self.notebook_json)
    notebook_json['snippets'] = [snippet_json]
    response = self.client.post(reverse('notebook:execute'), {'notebook': json.dumps(notebook_json), 'snippet': json.dumps(snippet_json)})
    data = json.loads(response.content)

    assert_equal(0, data['status'], data)
    assert_equal(1, data['handle']['statement_id'], data)
    assert_equal(2, data['handle']['statements_count'], data)
    assert_equal(False, data['handle']['has_more_statements'], data)
    assert_equal({'row': 1, 'column': 0}, data['handle']['start'], data)
    assert_equal({'row': 1, 'column': 33}, data['handle']['end'], data)


  def test_explain(self):
    response = self.client.post(reverse('notebook:explain'), {'notebook': self.notebook_json, 'snippet': self.snippet_json})
    data = json.loads(response.content)

    assert_equal(0, data['status'], data)
    assert_true('STAGE DEPENDENCIES' in data['explanation'], data)
    assert_equal(self.statement, data['statement'], data)


  def test_get_sample(self):
    response = self.client.post(reverse('notebook:api_sample_data',
      kwargs={'database': 'default', 'table': 'sample_07'}),
      {'notebook': self.notebook_json, 'snippet': self.snippet_json})
    data = json.loads(response.content)

    assert_equal(0, data['status'], data)
    assert_true('headers' in data)
    assert_true('rows' in data)
    assert_true(len(data['rows']) > 0)

    response = self.client.post(reverse('notebook:api_sample_data_column',
      kwargs={'database': 'default', 'table': 'sample_07', 'column': 'code'}),
      {'notebook': self.notebook_json, 'snippet': self.snippet_json})
    data = json.loads(response.content)

    assert_equal(0, data['status'], data)
    assert_true('headers' in data)
    assert_equal(['code'], data['headers'])
    assert_true('rows' in data)
    assert_true(len(data['rows']) > 0)
