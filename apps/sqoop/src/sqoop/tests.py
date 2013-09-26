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

from sqoop.client.connection import Connection
from sqoop.client.job import Job
from sqoop.test_base import SqoopServerProvider

from nose.tools import assert_true, assert_equal


LOG = logging.getLogger(__name__)


CONNECTION_FORM_VALUES = {
  'connection.jdbcDriver': 'org.apache.derby.jdbc.EmbeddedDriver',
  'connection.connectionString': 'jdbc%3Aderby%3A%2Ftmp%2Ftest',
  'connection.username': 'abe',
  'connection.password': 'test',
  'connection.jdbcProperties': None
}

JOB_FORM_VALUES = {
  'table.schemaName': None,
  'table.tableName': 'test',
  'table.sql': None,
  'table.columns': 'name',
  'table.partitionColumn': 'id',
  'table.boundaryQuery': None,
  'table.partitionColumnNull': None
}

FRAMEWORK_FORM_VALUES = {
  'output.outputFormat': 'TEXT_FILE',
  'output.outputDirectory': '/tmp/test.out',
  'output.storageType': 'HDFS',
  'throttling.extractors': None,
  'throttling.loaders': None,
  'security.maxConnections': None
}

class TestSqoopServerBase(SqoopServerProvider):
  def create_connection(self, name='test1', connector_id=1):
    conn = Connection(name, connector_id)
    conn.framework = self.client.get_framework().con_forms
    conn.connector = self.client.get_connectors()[0].con_forms

    for _connector in conn.connector:
      for _input in _connector.inputs:
        if _input.name not in CONNECTION_FORM_VALUES:
          LOG.warning("Connection input mapping %s does not exist. Maybe it's new?" % _input.name)
        elif CONNECTION_FORM_VALUES[_input.name]:
          _input.value = CONNECTION_FORM_VALUES[_input.name]

    for _framework in conn.framework:
      for _input in _framework.inputs:
        if _input.name not in FRAMEWORK_FORM_VALUES:
          LOG.warning("Framework input mapping %s does not exist. Maybe it's new?" % _input.name)
        elif FRAMEWORK_FORM_VALUES[_input.name]:
          _input.value = FRAMEWORK_FORM_VALUES[_input.name]

    return self.client.create_connection(conn)

  def create_job(self, _type="IMPORT", name="test1", connection_id=1, connector_id=1):
    job = Job(_type, name, connection_id, connector_id)
    job.framework = self.client.get_framework().job_forms[_type]
    job.connector = self.client.get_connectors()[0].job_forms[_type]

    for _connector in job.connector:
      for _input in _connector.inputs:
        if _input.name not in JOB_FORM_VALUES:
          LOG.warning("Job input mapping %s does not exist. Maybe it's new?" % _input.name)
        elif JOB_FORM_VALUES[_input.name]:
          _input.value = JOB_FORM_VALUES[_input.name]

    for _framework in job.framework:
      for _input in _framework.inputs:
        if _input.name not in FRAMEWORK_FORM_VALUES:
          LOG.warning("Framework input mapping %s does not exist. Maybe it's new?" % _input.name)
        elif FRAMEWORK_FORM_VALUES[_input.name]:
          _input.value = FRAMEWORK_FORM_VALUES[_input.name]

    return self.client.create_job(job)

  def delete_sqoop_object(self, obj):
    if isinstance(obj, Connection):
      self.client.delete_connection(obj)
    elif isinstance(obj, Job):
      self.client.delete_job(obj)

  def delete_sqoop_objects(self, objects):
    for obj in objects:
      self.delete_sqoop_object(obj)

class TestSqoopClientConnections(TestSqoopServerBase):
  def test_connection(self):
    try:
      # Create
      conn = self.create_connection(name='conn1')
      conn2 = self.client.get_connection(conn.id)
      assert_true(conn2.id)
      assert_equal(conn.name, conn2.name)

      # Update
      conn2.name = 'conn-new-1'
      self.client.update_connection(conn2)
      conn3 = self.client.get_connection(conn2.id)
      assert_true(conn3.id)
      assert_equal(conn2.name, conn3.name)
    except:
      self.client.delete_connection(conn3)

  def test_get_connections(self):
    try:
      conn = self.create_connection(name='conn2')
      conns = self.client.get_connections()
      assert_true(len(conns) > 0)
    finally:
      self.client.delete_connection(conn)

class TestSqoopClientJobs(TestSqoopServerBase):
  def test_job(self):
    removable = []
    try:
      # Create
      conn = self.create_connection(name='conn3')
      removable.append(conn)
      job = self.create_job("IMPORT", "job1", connection_id=conn.id)
      removable.insert(0, job)
      assert_true(job.id)

      job2 = self.client.get_job(job.id)
      assert_true(job2.id)
      assert_equal(job.id, job2.id)

      # Update
      job.name = 'job-new-1'
      job3 = self.client.update_job(job)
      assert_equal(job.name, job3.name)
    finally:
      self.delete_sqoop_objects(removable)

  def test_get_jobs(self):
    removable = []
    try:
      conn = self.create_connection(name='conn4')
      removable.append(conn)
      job = self.create_job("IMPORT", "job2", connection_id=conn.id)
      removable.insert(0, job)
      assert_true(job.id)

      jobs = self.client.get_jobs()
      assert_true(len(jobs) > 0)
    finally:
      self.delete_sqoop_objects(removable)
