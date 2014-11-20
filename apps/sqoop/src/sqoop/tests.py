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

from sqoop.client.link import Link
from sqoop.client.job import Job
from sqoop.test_base import SqoopServerProvider

from nose.tools import assert_true, assert_equal
from nose.plugins.skip import SkipTest


LOG = logging.getLogger(__name__)


LINK_CONFIG_VALUES = {
  'linkConfig.jdbcDriver': 'org.apache.derby.jdbc.EmbeddedDriver',
  'linkConfig.String': 'jdbc%3Aderby%3A%2Ftmp%2Ftest',
  'linkConfig.username': 'abe',
  'linkConfig.password': 'test',
  'linkConfig.jdbcProperties': None
}

FROM_JOB_CONFIG_VALUES = {
  'fromJobConfig.schemaName': None,
  'fromJobConfig.tableName': 'test',
  'fromJobConfig.sql': None,
  'fromJobConfig.columns': 'name',
  'fromJobConfig.partitionColumn': 'id',
  'fromJobConfig.boundaryQuery': None,
  'fromJobConfig.allowNullValueInPartitionColumn': None
}

TO_JOB_CONFIG_VALUES = {
  'toJobConfig.outputFormat': 'TEXT_FILE',
  'toJobConfig.outputDirectory': '/tmp/test.out',
  'toJobConfig.storageType': 'HDFS'
}

DRIVER_CONFIG_VALUES = {
  'throttlingConfig.numExtractor': '3',
  'throttlingConfig.numLoaders': '3'
}

class TestSqoopServerBase(SqoopServerProvider):
  def create_link(self, name='test1', connector_id=1):
    link = Link(name, connector_id)
    link.linkConfig = self.client.get_connectors()[0].link_config

    for _config in link.linkConfig:
      for _input in _config.inputs:
        if _input.name not in LINK_CONFIG_VALUES:
          LOG.warning("Link config input mapping %s does not exist. Maybe it's new?" % _input.name)
        elif LINK_CONFIG_VALUES[_input.name]:
          _input.value = LINK_CONFIG_VALUES[_input.name]

    return self.client.create_link(link)

  def create_job(self, name="test1", from_link_id=1, to_link_id=2, from_connector_id=1, to_connector_id=2):
    job = Job( name, from_link_id, to_link_id, from_connector_id, to_connector_id)
    job.driver_config = self.client.get_driver().job_config
    job.from_config = self.client.get_connectors()[0].job_config['FROM']
    job.to_config = self.client.get_connectors()[0].job_config['TO']

    for _from_config in job.from_config:
        for _input in _from_config.inputs:
            if _input.name not in FROM_JOB_CONFIG_VALUES:
                LOG.warning("From Job config input mapping %s does not exist. Maybe it's new?" % _input.name)
            elif FROM_JOB_CONFIG_VALUES[_input.name]:
                _input.value = FROM_JOB_CONFIG_VALUES[_input.name]

    for _to_config in job.to_config:
        for _input in _to_config.inputs:
            if _input.name not in TO_JOB_CONFIG_VALUES:
                LOG.warning("To Job config input mapping. Maybe it's new?" % _input.name)
            elif TO_JOB_CONFIG_VALUES[_input.name]:
                _input.value = TO_JOB_CONFIG_VALUES[_input.name]

    for _driver_config in job.driver_config:
        for _input in _driver_config.inputs:
            if _input.name not in DRIVER_CONFIG_VALUES:
                LOG.warning("Driver Job config input mapping. Maybe it's new?" % _input.name)
            elif DRIVER_CONFIG_VALUES[_input.name]:
                _input.value = DRIVER_CONFIG_VALUES[_input.name]

    return self.client.create_job(job)

  def delete_sqoop_object(self, obj):
    if isinstance(obj, Link):
      self.client.delete_link(obj)
    elif isinstance(obj, Job):
      self.client.delete_job(obj)

  def delete_sqoop_objects(self, objects):
    for obj in objects:
      self.delete_sqoop_object(obj)

class TestSqoopClientLinks(TestSqoopServerBase):
  def test_link(self):
    raise SkipTest
    try:
      # Create
      link = self.create_link(name='link1')
      link2 = self.client.get_link(link.id)
      assert_true(link2.id)
      assert_equal(link.name, link2.name)

      # Update
      link2.name = 'link-new-1'
      self.client.update_link(link2)
      link3 = self.client.get_link(link2.id)
      assert_true(link3.id)
      assert_equal(link3.name, link3.name)
    except:
      self.client.delete_link(link3)

  def test_get_links(self):
    raise SkipTest
    try:
      link = self.create_link(name='link2')
      links = self.client.get_links()
      assert_true(len(links) > 0)
    finally:
      self.client.delete_link(link)

class TestSqoopClientJobs(TestSqoopServerBase):
  def test_job(self):
    raise SkipTest
    removable = []
    # Create
    from_link = self.create_link(name='link3from')
    to_link = self.create_link(name='link3to')

    try:
      removable.append(from_link)
      removable.append(to_link)

      job = self.create_job("job1", from_link_id=from_link.id, to_link_id=to_link.id)
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
    raise SkipTest
    removable = []
    from_link = self.create_link(name='link4from')
    to_link = self.create_link(name='link4to')
    try:

      removable.append(from_link)
      removable.append(to_link)

      job = self.create_job("job2", from_link_id=from_link.id, to_link_id=to_link.id)
      removable.insert(0, job)
      assert_true(job.id)

      jobs = self.client.get_jobs()
      assert_true(len(jobs) > 0)
    finally:
      self.delete_sqoop_objects(removable)
