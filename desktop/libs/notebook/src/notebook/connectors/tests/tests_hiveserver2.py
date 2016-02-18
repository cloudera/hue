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
import re

from nose.tools import assert_equal, assert_true, assert_false

from django.contrib.auth.models import User

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import add_to_group, grant_access
from notebook.connectors.hiveserver2 import HS2Api

from beeswax.server import dbms
from beeswax.test_base import get_query_server_config


class TestNotebookApi(object):

  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="test", recreate=False, is_superuser=False)
    self.user = User.objects.get(username='test')
    add_to_group('test')
    grant_access("test", "test", "notebook")

    self.db = dbms.get(self.user, get_query_server_config())
    #self.cluster.fs.do_as_user('test', self.cluster.fs.create_home_dir, '/user/test')
    self.api = HS2Api(self.user)


  def test_prepare_hql_query(self):
    statement = "SELECT myUpper(description) FROM sample_07 LIMIT 10"
    snippet_json = """
        {
            "status": "running",
            "database": "default",
            "properties": {
                "files": [{
                    "path": "/user/test/myudfs.jar",
                    "type": "jar"
                }],
                "functions": [{
                    "class_name": "org.hue.udf.MyUpper",
                    "name": "myUpper"
                }],
                "settings": [{
                    "value": "spark",
                    "key": "hive.execution.engine"
                }]
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

    snippet = json.loads(snippet_json)
    hql_query = self.api._prepare_hql_query(snippet, statement)

    assert_equal([{'key': 'hive.execution.engine', 'value': 'spark'}], hql_query.settings)
    assert_equal([{'type': 'jar', 'path': '/user/test/myudfs.jar'}], hql_query.file_resources)
    assert_equal([{'name': 'myUpper', 'class_name': 'org.hue.udf.MyUpper'}], hql_query.functions)

    config_statements = ', '.join(hql_query.get_configuration_statements())

    pattern = re.compile("ADD JAR hdfs://[A-Za-z0-9.:_-]+/user/test/myudfs.jar")
    assert_true(pattern.search(config_statements), config_statements)
    assert_true("CREATE TEMPORARY FUNCTION myUpper AS 'org.hue.udf.MyUpper'" in config_statements, config_statements)
