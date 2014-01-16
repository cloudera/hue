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

import cStringIO
import os

from nose.tools import assert_true, assert_equal, assert_false
from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest

from desktop.lib.django_test_util import make_logged_in_client
from hadoop import cluster
from hadoop import conf
from hadoop import confparse
from hadoop import pseudo_hdfs4


@attr('requires_hadoop')
def test_live_jobtracker():
  """
  Checks that LiveJobTracker never raises
  exceptions for most of its calls.
  """
  raise SkipTest

  minicluster = pseudo_hdfs4.shared_cluster()

  jt = minicluster.jt
  # Make sure that none of the following
  # raise.
  assert_true(jt.queues())
  assert_true(jt.cluster_status())
  assert_true(jt.all_task_trackers())
  assert_true(jt.active_trackers())
  assert_true(jt.blacklisted_trackers())
  # not tested: task_tracker
  assert_true(jt.running_jobs())
  assert_true(jt.completed_jobs())
  assert_true(jt.failed_jobs())
  assert_true(jt.all_jobs())
  # not tested: get_job_counters
  assert_true(jt.get_current_time())
  # not tested: get_job_xml


def test_confparse():
  data = """
    <configuration>
      <property>
        <name>fs.default.name</name>
        <value>hdfs://localhost:8020</value>
      </property>
      <property>
        <name>with_description</name>
        <value>bar</value>
        <description>A base for other temporary directories.</description>
      </property>
      <property>
        <name>boolean_true</name>
        <value>true</value>
      </property>
      <property>
        <name>boolean_false</name>
        <value>false</value>
      </property>
    </configuration>
  """

  cp_data = confparse.ConfParse(data)
  cp_file = confparse.ConfParse(cStringIO.StringIO(data))

  for cp in (cp_data, cp_file):
    assert_equal(cp['fs.default.name'], 'hdfs://localhost:8020')
    assert_equal(cp.get('with_description'), 'bar')
    assert_equal(cp.get('not_in_xml', 'abc'), 'abc')
    assert_equal(cp.getbool('boolean_true'), True)
    assert_equal(cp.getbool('boolean_false'), False)
    assert_equal(cp.getbool('not_in_xml', True), True)

    try:
      cp['bogus']
      assert_true(False, 'Should not get here')
    except KeyError, kerr:
      ex = kerr

  cp_empty = confparse.ConfParse("")
  assert_equal(cp_empty.get('whatever', 'yes'), 'yes')

def test_tricky_confparse():
  """
  We found (experimentally) that dealing with a file
  sometimes triggered the wrong results here.
  """
  cp_data = confparse.ConfParse(file(os.path.join(os.path.dirname(__file__),
                                                  "test_data",
                                                  "sample_conf.xml")))
  assert_equal("org.apache.hadoop.examples.SleepJob", cp_data["mapred.mapper.class"])


def test_config_validator_basic():
  reset = (
    conf.HDFS_CLUSTERS['default'].WEBHDFS_URL.set_for_testing('http://not.the.re:50070/'),
    conf.MR_CLUSTERS['default'].JT_THRIFT_PORT.set_for_testing(70000),
  )
  old = cluster.clear_caches()
  try:
    cli = make_logged_in_client()
    resp = cli.get('/desktop/debug/check_config')
    assert_true('hadoop.hdfs_clusters.default.webhdfs_url' in resp.content)
  finally:
    for old_conf in reset:
      old_conf()
    cluster.restore_caches(old)


@attr('requires_hadoop')
def test_config_validator_more():
  # TODO: Setup DN to not load the plugin, which is a common user error.

  # We don't actually use the mini_cluster. But the cluster sets up the correct
  # configuration that forms the test basis.
  minicluster = pseudo_hdfs4.shared_cluster()
  cli = make_logged_in_client()

  reset = (
    conf.MR_CLUSTERS["default"].HOST.set_for_testing("localhost"),
    conf.MR_CLUSTERS['default'].JT_THRIFT_PORT.set_for_testing(23),
  )
  old = cluster.clear_caches()
  try:
    resp = cli.get('/debug/check_config')

    assert_false('Failed to access filesystem root' in resp.content)
    assert_false('Failed to create' in resp.content)
    assert_false('Failed to chown' in resp.content)
    assert_false('Failed to delete' in resp.content)
  finally:
    for old_conf in reset:
      old_conf()
    cluster.restore_caches(old)


def test_non_default_cluster():
  NON_DEFAULT_NAME = 'non_default'
  old = cluster.clear_caches()
  reset = (
    conf.HDFS_CLUSTERS.set_for_testing({ NON_DEFAULT_NAME: { } }),
    conf.MR_CLUSTERS.set_for_testing({ NON_DEFAULT_NAME: { } }),
  )
  try:
    # This is indeed the only hdfs/mr cluster
    assert_equal(1, len(cluster.get_all_hdfs()))
    assert_equal(1, len(cluster.all_mrclusters()))
    assert_true(cluster.get_hdfs(NON_DEFAULT_NAME))
    assert_true(cluster.get_mrcluster(NON_DEFAULT_NAME))

    cli = make_logged_in_client()
    # That we can get to a view without errors means that the middlewares work
    cli.get('/about')
  finally:
    for old_conf in reset:
      old_conf()
    cluster.restore_caches(old)
