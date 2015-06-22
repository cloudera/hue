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

import os
import shutil
import tempfile

from nose.tools import assert_true, assert_equal, assert_false

from sqoop.conf import SQOOP_CONF_DIR
from sqoop.client.base import SqoopClient
from sqoop.sqoop_properties import reset


def test_security_plain():
  tmpdir = tempfile.mkdtemp()
  finish = SQOOP_CONF_DIR.set_for_testing(tmpdir)

  try:
    xml = sqoop_properties(authentication='SIMPLE')
    with file(os.path.join(tmpdir, 'sqoop.properties'), 'w') as f:
      f.write(xml)
    reset()

    client = SqoopClient('test.com', 'test')
    assert_false(client._security_enabled)
  finally:
    reset()
    finish()
    shutil.rmtree(tmpdir)


def test_security_kerberos():
  tmpdir = tempfile.mkdtemp()
  finish = SQOOP_CONF_DIR.set_for_testing(tmpdir)

  try:
    xml = sqoop_properties(authentication='KERBEROS')
    with file(os.path.join(tmpdir, 'sqoop.properties'), 'w') as f:
      f.write(xml)
    reset()

    client = SqoopClient('test.com', 'test')
    assert_true(client._security_enabled)
  finally:
    reset()
    finish()
    shutil.rmtree(tmpdir)


def sqoop_properties(authentication='SIMPLE'):

  return """
org.apache.sqoop.repository.provider=org.apache.sqoop.repository.JdbcRepositoryProvider
org.apache.sqoop.repository.jdbc.transaction.isolation=READ_COMMITTED
org.apache.sqoop.repository.jdbc.maximum.connections=10
org.apache.sqoop.repository.jdbc.handler=org.apache.sqoop.repository.derby.DerbyRepositoryHandler
org.apache.sqoop.repository.jdbc.url=jdbc:derby:/var/lib/sqoop2/repository/db;create=true
org.apache.sqoop.repository.jdbc.driver=org.apache.derby.jdbc.EmbeddedDriver
org.apache.sqoop.repository.jdbc.create.schema=true
org.apache.sqoop.repository.jdbc.user=sa
org.apache.sqoop.repository.jdbc.password=
org.apache.sqoop.repository.sysprop.derby.stream.error.file=/var/log/sqoop2/derbyrepo.log
org.apache.sqoop.submission.engine=org.apache.sqoop.submission.mapreduce.MapreduceSubmissionEngine
org.apache.sqoop.submission.engine.mapreduce.configuration.directory={{CMF_CONF_DIR}}/yarn-conf
org.apache.sqoop.execution.engine=org.apache.sqoop.execution.mapreduce.MapreduceExecutionEngine
org.apache.sqoop.security.authentication.type=%(authentication)s
org.apache.sqoop.security.authentication.handler=org.apache.sqoop.security.KerberosAuthenticationHandler
org.apache.sqoop.security.authentication.kerberos.principal=sqoop2/_HOST@VPC.CLOUDERA.COM
org.apache.sqoop.security.authentication.kerberos.http.principal=HTTP/_HOST@VPC.CLOUDERA.COM
org.apache.sqoop.security.authentication.kerberos.keytab=sqoop.keytab
org.apache.sqoop.security.authentication.kerberos.http.keytab=sqoop.keytab
  """ % {
    'authentication': authentication,
  }
