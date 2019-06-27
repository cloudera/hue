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

from future import standard_library
standard_library.install_aliases()
from builtins import next
from builtins import map
from builtins import str
from builtins import chr
from builtins import range
from builtins import object
import gzip
import json
import logging
import os
import random
import re
import shutil
import socket
import string
import sys
import tempfile
import threading

import hadoop

from nose.tools import assert_true, assert_equal, assert_false, assert_not_equal, assert_raises
from nose.plugins.skip import SkipTest

from django.utils.encoding import smart_str
from django.utils.html import escape
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import transaction

from desktop.lib.exceptions_renderable import PopupException
from desktop.conf import \
    AUTH_USERNAME as DEFAULT_AUTH_USERNAME, \
    AUTH_PASSWORD as DEFAULT_AUTH_PASSWORD, \
    AUTH_PASSWORD_SCRIPT as DEFAULT_AUTH_PASSWORD_SCRIPT, \
    LDAP_USERNAME, \
    LDAP_PASSWORD, \
    USE_NEW_EDITOR
from desktop import redaction
from desktop.redaction import logfilter
from desktop.redaction.engine import RedactionPolicy, RedactionRule
from desktop.lib.django_test_util import make_logged_in_client, assert_equal_mod_whitespace
from desktop.lib.parameterization import substitute_variables
from desktop.lib.test_utils import grant_access, add_to_group
from desktop.lib.security_util import get_localhost_name
from desktop.lib.test_export_csvxls import _read_xls_sheet_data
from hadoop.fs.hadoopfs import Hdfs

from hadoop import ssl_client_site
from hadoop.pseudo_hdfs4 import is_live_cluster

import desktop.conf as desktop_conf

import beeswax.create_table
import beeswax.hive_site
import beeswax.models
import beeswax.views

from beeswax import conf, hive_site
from beeswax.common import apply_natural_sort
from beeswax.conf import HIVE_SERVER_HOST, AUTH_USERNAME, AUTH_PASSWORD, AUTH_PASSWORD_SCRIPT
from beeswax.views import collapse_whitespace, _save_design, parse_out_jobs
from beeswax.test_base import make_query, wait_for_query_to_finish, verify_history, get_query_server_config,\
  fetch_query_result_data
from beeswax.design import hql_query
from beeswax.data_export import upload, download
from beeswax.models import SavedQuery, QueryHistory, HQL, HIVE_SERVER2
from beeswax.server import dbms
from beeswax.server.dbms import QueryServerException
from beeswax.server.hive_server2_lib import HiveServerClient,\
  PartitionKeyCompatible, PartitionValueCompatible, HiveServerTable,\
  HiveServerTColumnValue2
from beeswax.test_base import BeeswaxSampleProvider, is_hive_on_spark, get_available_execution_engines
from beeswax.hive_site import get_metastore, hiveserver2_jdbc_url

if sys.version_info[0] > 2:
  from io import StringIO as string_io
else:
  from cStringIO import StringIO as string_io

LOG = logging.getLogger(__name__)

def _list_dir_without_temp_files(fs, target_dir):
  return [f for f in fs.listdir(target_dir) if not f.startswith('.')]

def _make_query(client, query, submission_type="Execute",
                udfs=None, settings=None, resources=[],
                wait=False, name=None, desc=None, local=True,
                is_parameterized=True, max=30.0, database='default', email_notify=False, params=None, server_name='beeswax', **kwargs):

  res = make_query(client, query, submission_type,
                   udfs, settings, resources,
                   wait, name, desc, local, is_parameterized, max, database, email_notify, params, server_name, **kwargs)

  # Should be in the history if it's submitted.
  if submission_type == 'Execute':
    if is_parameterized and params:
      query = substitute_variables(query, dict(params))
    fragment = collapse_whitespace(smart_str(escape(query[:20])))
    verify_history(client, fragment=fragment, server_name=server_name)

  return res

def random_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def get_csv(client, result_response):
  """Get the csv for a query result"""
  content = json.loads(result_response.content)
  assert_true(content['isSuccess'])
  csv_link = '/beeswax/download/%s/csv' % content['id']
  csv_resp = client.get(csv_link)
  return ''.join(csv_resp.streaming_content)


class TestBeeswaxWithHadoop(BeeswaxSampleProvider):
  requires_hadoop = True
  integration = True

  def setUp(self):
    self.user = User.objects.get(username='test')
    add_to_group('test')
    self.db = dbms.get(self.user, get_query_server_config())
    self.cluster.fs.do_as_user('test', self.cluster.fs.create_home_dir, '/user/test')

  def _verify_query_state(self, state, *extra_states):
    """
    Verify the state of the latest query.
    Return the id of that query
    """
    resp = self.client.get('/beeswax/query_history')
    history = resp.context[0]['page'].object_list[0]
    last_state = history.last_state
    assert_true(last_state in (state,) + extra_states)
    return history.id


  def test_query_with_error(self):
    # Creating a table "again" should not work; error should be displayed.
    response = _make_query(self.client, "CREATE TABLE test (foo INT)", database=self.db_name, wait=True)
    content = json.loads(response.content)
    assert_true("AlreadyExistsException" in content.get('message'), content)


  def test_query_with_resource(self):
    udf = self.cluster.fs_prefix + "/square.py"
    script = self.cluster.fs.open(udf, "w")
    script.write(
      """#!/usr/bin/python
import sys
for x in sys.stdin:
  val = int(x)
  print val*val
""")
    script.close()

    response = _make_query(self.client,
      "SELECT TRANSFORM (foo) USING 'python square.py' AS b FROM test",
      resources=[("FILE", udf)], local=False, database=self.db_name)
    response = wait_for_query_to_finish(self.client, response, max=180.0)
    content = fetch_query_result_data(self.client, response)
    assert_equal([['0'], ['1'], ['4'], ['9']], content["results"][0:4])


  def test_query_with_setting(self):
    table_name = 'test_query_with_setting'
    response = _make_query(self.client, "CREATE TABLE `%(db)s`.`%(table_name)s` AS SELECT foo+1 FROM test WHERE foo=4" % {'db': self.db_name, 'table_name': table_name},
      settings=[("mapred.job.name", "test_query_with_setting"),
        ("hive.exec.compress.output", "true")], local=False, database=self.db_name) # Run on MR, because that's how we check it worked.
    response = wait_for_query_to_finish(self.client, response, max=180.0)
    # Check that we actually got a compressed output
    table = self.db.get_table(database=self.db_name, table_name=table_name)
    hdfs_loc = Hdfs.urlsplit(table.path_location)

    files = self.cluster.fs.listdir(hdfs_loc[2])
    assert_true(len(files) >= 1, files)
    assert_true(files[0].endswith(".deflate"), files[0])

    raise SkipTest
    # And check that the name is right...
    assert_true("test_query_with_setting" in [ x.profile.name for x in self.cluster.jt.all_jobs().jobs ])

    # While we're at it, check that we're running jobs as the correct user on MR.
    assert_equal("test",
      [ x.profile for x in self.cluster.jt.all_jobs().jobs
        if x.profile.name == "test_query_with_setting" ][0].user)


  def test_lazy_query_status_update(self):
    QUERY = """
      SELECT MIN(foo), MAX(foo), SUM(foo) FROM test;
    """
    wait_for_query_to_finish(self.client, _make_query(self.client, QUERY, local=False, database=self.db_name), max=180.0)
    self._verify_query_state(beeswax.models.QueryHistory.STATE.available.value)

    # Make sure expired query states are lazily updated.
    resp = self.client.get('/beeswax/query_history')
    history = resp.context[0]['page'].object_list[0]
    self.db.close_operation(history.get_full_object().get_handle())
    resp = self.client.get("/beeswax/execute/query/%s" % history.id)
    assert_true(resp.status_code, 302)

    resp = self.client.get('/beeswax/query_history')
    history = resp.context[0]['page'].object_list[0]
    assert_equal(history.last_state, beeswax.models.QueryHistory.STATE.expired.value)


  def test_basic_flow(self):
    # Minimal server operation
    databases = self.db.get_databases()
    assert_true('default' in databases, databases)
    assert_true(self.db_name in databases, databases)
    assert_true('%s_other' % self.db_name in databases, databases)

    # Use GROUP BY to trigger MR job
    QUERY = """
      SELECT MIN(foo), MAX(foo), SUM(foo) FROM test;
    """
    response = _make_query(self.client, QUERY, local=False, database=self.db_name)
    content = json.loads(response.content)
    assert_true('watch_url' in content)

    # Check that we report this query as "running" (this query should take a little while).
    if not is_hive_on_spark():
      self._verify_query_state(beeswax.models.QueryHistory.STATE.running.value, beeswax.models.QueryHistory.STATE.available.value)

    response = wait_for_query_to_finish(self.client, response, max=180.0)
    content = fetch_query_result_data(self.client, response)

    assert_equal([0, 255, 32640], content["results"][0], content["results"][0])
    assert_equal(['INT_TYPE', 'INT_TYPE', 'BIGINT_TYPE'], [col['type'] for col in content["columns"]])
    self._verify_query_state(beeswax.models.QueryHistory.STATE.available.value)

    # Query multi-page request
    QUERY = """
      SELECT * FROM test
    """
    response = _make_query(self.client, QUERY, name='select star', local=False, database=self.db_name)
    response = wait_for_query_to_finish(self.client, response)
    content = fetch_query_result_data(self.client, response)

    assert_true([99, u'0x63'] in content['results'], content['results'])
    assert_true(content["has_more"])
    response = self.client.get("/beeswax/results/%s/%s?format=json" % (content["id"], content["next_row"]))
    content = json.loads(response.content)
    assert_true([199, u'0xc7'] in content['results'], content['results'])
    response = self.client.get("/beeswax/results/%s/0?format=json" % (content["id"]))
    content = json.loads(response.content)
    assert_true([99, u'0x63'] in content['results'])
    assert_equal(0, len(content["hadoop_jobs"]), "SELECT * shouldn't have started jobs.")

    # Download the data
    response = self.client.get(content["download_urls"]["csv"])
    # Header line plus data lines...
    assert_equal(257, ''.join(response.streaming_content).count("\n"))


  def test_api_get_session(self):
    session = None
    try:
      # Create open session
      session = self.db.open_session(self.user)

      resp = self.client.get(reverse("beeswax:api_get_session"))
      data = json.loads(resp.content)
      assert_true('properties' in data, data)
      assert_true('session' in data, data)
      assert_true('id' in data['session'], data['session'])
    finally:
      if session is not None:
        try:
          self.db.close_session(session)
        except Exception:
          pass


  def test_api_close_session(self):
    session = None
    try:
      # Create open session
      session = self.db.open_session(self.user)

      resp = self.client.post(reverse("beeswax:api_close_session", kwargs={'session_id': session.id}))
      data = json.loads(resp.content)
      assert_equal(0, data['status'])
      assert_true('session' in data)
      assert_equal(4, data['session']['status'])

      # Closed sessions will return error response
      resp = self.client.post(reverse("beeswax:api_close_session", kwargs={'session_id': session.id}))
      data = json.loads(resp.content)
      assert_equal(-1, data['status'])
    finally:
      if session is not None:
        try:
          self.db.close_session(session)
        except Exception:
          pass


  def test_result_escaping(self):
    # Check for XSS and NULL display
    QUERY = """
      SELECT 'abc', 1.0, 1=1, 1, 1/0, '<a>lala</a>lulu', 'some   spaces' from test LIMIT 3;
    """
    response = _make_query(self.client, QUERY, local=False, database=self.db_name)
    content = json.loads(response.content)
    assert_true('watch_url' in content)

    response = wait_for_query_to_finish(self.client, response, max=180.0)
    content = fetch_query_result_data(self.client, response)

    assert_equal([
        [u'abc', 1.0, True, 1, u'NULL', u'&lt;a&gt;lala&lt;/a&gt;lulu', 'some&nbsp;&nbsp;&nbsp;spaces'],
        [u'abc', 1.0, True, 1, u'NULL', u'&lt;a&gt;lala&lt;/a&gt;lulu', 'some&nbsp;&nbsp;&nbsp;spaces'],
        [u'abc', 1.0, True, 1, u'NULL', u'&lt;a&gt;lala&lt;/a&gt;lulu', 'some&nbsp;&nbsp;&nbsp;spaces'],
      ], content["results"], content)


  def test_result_nullification(self):
    QUERY = """
      CREATE TABLE test_result_nullification (a int);
      INSERT INTO TABLE test_result_nullification
      VALUES
      (1), (1), (1), (1), (1), (1), (1), (1),
      (2), (2), (2), (2), (2), (2), (2), (2),
      (NULL), (3), (3), (3), (3), (3), (3), (3),
      (4), (4), (4), (4), (4), (4), (4), (4),
      (5), (5), (5), (5), (5), (5), (5), (5),
      (6), (6), (6), (6), (6), (6), (6), (6);
    """
    response = _make_query(self.client, QUERY, local=False, database=self.db_name)
    content = json.loads(response.content)
    assert_true('watch_url' in content)

    response = wait_for_query_to_finish(self.client, response, max=180.0)
    content = fetch_query_result_data(self.client, response)

    QUERY = """
      SELECT * FROM test_result_nullification;
    """
    response = _make_query(self.client, QUERY, local=False, database=self.db_name)
    content = json.loads(response.content)
    assert_true('watch_url' in content)

    response = wait_for_query_to_finish(self.client, response, max=180.0)
    content = fetch_query_result_data(self.client, response)

    assert_equal([
        [1], [1], [1], [1], [1], [1], [1], [1],
        [2], [2], [2], [2], [2], [2], [2], [2],
        [u'NULL'], [3], [3], [3], [3], [3], [3], [3],
        [4], [4], [4], [4], [4], [4], [4], [4],
        [5], [5], [5], [5], [5], [5], [5], [5],
        [6], [6], [6], [6], [6], [6], [6], [6]
      ], content["results"], content)


  def test_query_with_udf(self):
    """
    Testing query with udf
    """
    execution_engines = get_available_execution_engines()

    for engine in execution_engines:
      response = _make_query(self.client, "SELECT my_sqrt(foo), my_float(foo) FROM test where foo=4 GROUP BY foo", # Force MR job with GROUP BY
        udfs=[('my_sqrt', 'org.apache.hadoop.hive.ql.udf.UDFSqrt'),
              ('my_float', 'org.apache.hadoop.hive.ql.udf.UDFToFloat')],
        local=False, database=self.db_name, settings=[('hive.execution.engine', engine)])
      response = wait_for_query_to_finish(self.client, response, max=60.0)
      content = fetch_query_result_data(self.client, response)

      assert_equal([2.0, 4.0], content["results"][0])
      log = content['log']

      assert_true(search_log_line('Completed executing command', log), log)
      # Test job extraction while we're at it
      assert_equal(1, len(parse_out_jobs(log, engine)), "Should have started 1 job and extracted it.")


  def test_query_with_remote_udf(self):
    """
    UDF is on HDFS.  This was implemented as part of HIVE-1157.
    """
    # BeeswaxTest.jar is gone
    raise SkipTest

    src = file(os.path.join(os.path.dirname(__file__), "..", "..", "java-lib", "BeeswaxTest.jar"))
    udf = self.cluster.fs_prefix + "hive1157.jar"
    dest = self.cluster.fs.open(udf, "w")
    shutil.copyfileobj(src, dest)
    dest.close()
    src.close()

    # Beware that this doesn't work with mapred.job.tracker=local :/
    response = _make_query(self.client, "SELECT cube(foo) FROM test WHERE foo=4",
      udfs=[('cube', 'com.cloudera.beeswax.CubeSampleUDF')],
      resources=[('JAR', udf)], local=False, database=self.db_name)
    response = wait_for_query_to_finish(self.client, response, max=60.0)
    assert_equal(["64"], response.context[0]["results"][0])


  def test_query_with_simple_errors(self):
    hql = "SELECT KITTENS ARE TASTY"
    resp = _make_query(self.client, hql, name='tasty kittens', wait=False, local=False, database=self.db_name)
    assert_true("ParseException line" in json.loads(resp.content)["message"])

    # Watch page will fail as operationHandle=None
    self._verify_query_state(beeswax.models.QueryHistory.STATE.failed.value)


  def test_sync_query_exec(self):
    # Execute Query Synchronously, set fetch size and fetch results
    # verify the size of resultset,
    hql = """
      SELECT foo FROM `%(db)s`.`test`;
    """ % {'db': self.db_name}
    query = hql_query(hql)
    handle = self.db.execute_and_wait(query)

    results = self.db.fetch(handle, True, 5)
    row_list = list(results.rows())
    assert_equal(len(row_list), 5)

    self.db.close(handle)


  def test_sync_query_error(self):
    # We don't use synchronous queries anywhere.
    # It used to call BeeswaxService.executeAndWait()
    raise SkipTest
    # Execute incorrect Query , verify the error code and sqlstate
    hql = """
      SELECT FROM `%(db)s`.`zzzzz`
    """ % {'db': self.db_name}
    query = hql_query(hql)
    try:
      self.db.execute_and_wait(query)
    except QueryServerException as bex:
      assert_equal(bex.errorCode, 40000)
      assert_equal(bex.SQLState, "42000")


  def test_fetch_configuration(self):
    class MockClient(object):
      """Check if sent fetch correctly supports start_over."""
      def __init__(self, support_start_over):
        self.support_start_over = support_start_over

      def fetch(self, query_id, start_over, fetch_size):
        assert_equal(self.support_start_over, start_over)
        class Result(object): pass
        res = Result()
        res.ready = False
        return res

    class ConfigVariable(object):
      def __init__(self, **entries):
        self.__dict__.update(entries)

    client = self.db

    prev_get_default_configuration = client.get_default_configuration
    prev_client = client.client

    try:
      client.client = MockClient(True)
      client.get_default_configuration = lambda a: []
      client.fetch(None, True, 5)

      client.client = MockClient(False)
      client.get_default_configuration = lambda a: []
      client.fetch(None, False, 5)

      client.client = MockClient(True)
      client.get_default_configuration = lambda a: [ConfigVariable(key='support_start_over', value='true')]
      client.fetch(None, True, 5)

      client.client = MockClient(False)
      client.get_default_configuration = lambda a: [ConfigVariable(key='support_start_over', value='false')]
      client.fetch(None, True, 5)
    finally:
      client.get_default_configuration = prev_get_default_configuration
      client.client = prev_client


  def test_parameterization(self):
    #@TODO@ Prakash fix this test
    raise SkipTest
    response = _make_query(self.client, "SELECT foo FROM test WHERE foo='$x' and bar='$y'", is_parameterized=False, database=self.db_name)
    content = json.loads(response.content)
    # Assert no parameterization was offered
    assert_true('watch_url' in content, content)

    data = {
      'query-query': "SELECT foo FROM test WHERE foo='$x' and bar='$y'",
      'query-database': self.db_name
    }
    response = self.client.post(reverse('beeswax:api_parameters'), data)
    content = json.loads(response.content)
    assert_equal([
        {'parameter': 'parameterization-x', 'name': 'x'},
        {'parameter': 'parameterization-y', 'name': 'y'}
      ], content['parameters'], content)

    # Now fill it out
    response = _make_query(self.client, "SELECT foo FROM test WHERE foo='$x' and bar='$y'", params=[('x', '1'), ('y', '2')], database=self.db_name)
    content = json.loads(response.content)
    assert_true('watch_url' in content, content)
    query_history = QueryHistory.get(content['id'])

    # Check that substitution happened!
    assert_equal("SELECT foo FROM test WHERE foo='1' and bar='2'", query_history.query)

    # Check that error handling is reasonable
    response = _make_query(self.client, "SELECT foo FROM test WHERE foo='$x' and bar='$y'", params=[('x', "'_this_is_not SQL "), ('y', '2')], database=self.db_name)
    content = json.loads(response.content)
    assert_true("FAILED: ParseException" in content.get('message'), content)

    # Check multi DB with a non default DB
    other_db = '%s_other' % self.db_name
    response = _make_query(self.client, "CREATE TABLE test (foo INT, bar STRING)", database=other_db)
    response = wait_for_query_to_finish(self.client, response)
    response = _make_query(self.client, "SELECT foo FROM test WHERE foo='$x' and bar='$y'", database=other_db)

    response = _make_query(self.client, "SELECT foo FROM test WHERE foo='$x' and bar='$y'", database=other_db,
                           params=[('x', '1'), ('y', '2')])
    content = json.loads(response.content)
    assert_true('watch_url' in content, content)
    query_history = QueryHistory.get(content['id'])
    assert_equal(other_db, query_history.design.get_design().query['database'])


  def test_explain_query(self):
    c = self.client
    response = _make_query(c, "SELECT KITTENS ARE TASTY", submission_type="Explain", database=self.db_name)
    assert_true("ParseException line" in json.loads(response.content)["message"])
    CREATE_TABLE = "CREATE TABLE `%(db)s`.`test_explain` (foo INT, bar STRING);" % {'db': self.db_name}
    response = _make_query(c, CREATE_TABLE, database=self.db_name)
    wait_for_query_to_finish(c, response)

    response = _make_query(c, "SELECT SUM(foo) FROM `%(db)s`.`test_explain`" % {'db': self.db_name}, settings=[('hive.explain.user', 'false')], submission_type="Explain") # Need to prefix database in Explain
    explanation = json.loads(response.content)['explanation']
    assert_true('STAGE DEPENDENCIES:' in explanation, explanation)
    assert_true('STAGE PLANS:' in explanation, explanation)


  def test_explain_query_i18n(self):
    if is_live_cluster():
      raise SkipTest('HUE-2884: Skipping test because we cannot guarantee live cluster supports utf8')

    query = u"SELECT foo FROM `%(db)s`.`test_utf8` WHERE bar='%(val)s'" % {'val': chr(200), 'db': self.db_name}
    response = _make_query(self.client, query, settings=[('hive.explain.user', 'false')], submission_type="Explain")
    explanation = json.loads(response.content)['explanation']
    assert_true('STAGE DEPENDENCIES:' in explanation, explanation)
    assert_true('STAGE PLANS:' in explanation, explanation)


  def test_query_i18n(self):
    # Test fails because HIVE_PLAN cannot be found and raises FileNotFoundException
    # because of a Hive bug.
    raise SkipTest

    # Selecting from utf-8 table should get correct result
    query = u"SELECT * FROM `%(db)s`.`test_utf8` WHERE bar='%(val)s'" % {'val': chr(200), 'db': self.db_name}
    response = _make_query(self.client, query, wait=True, database=self.db_name)
    assert_equal(["200", chr(200)], response.context[0]["results"][0], "selecting from utf-8 table should get correct result")

    csv = get_csv(self.client, response)
    assert_equal('"200","%s"' % (chr(200).encode('utf-8'),), csv.split()[1])

    # Selecting from latin1 table should not blow up
    query = u"SELECT * FROM `%(db)s`.`test_latin1` WHERE bar='%(val)s'" % {'val': chr(200), 'db': self.db_name}
    response = _make_query(self.client, query, wait=True, database=self.db_name)
    assert_true('results' in response.context, "selecting from latin1 table should not blow up")

    # Describe table should be fine with non-ascii comment
    response = self.client.get('/beeswax/table/%(db)s/test_utf8' % {'db': self.db_name})
    assert_equal(response.context[0]['table'].parameters['comment'], self.get_i18n_table_comment())


  def _parallel_query_helper(self, i, result_holder, lock, num_tasks):
    client = make_logged_in_client()
    try:
      q = "SELECT foo+" + str(i + 1) + " FROM test WHERE foo < 2"
      LOG.info("Starting " + str(i) + ": " + q)
      response = _make_query(client, q, local=False)
      response = wait_for_query_to_finish(client, response, max=(240.0 * num_tasks))
      lock.acquire()
      result_holder[i] = response
      lock.release()
      LOG.info("Finished: " + str(i))
    except Exception as e:
      LOG.exception("Saw exception in child thread: %s" % e)


  def test_multiple_statements_no_result_set(self):
    hql = """
      CREATE TABLE test_multiple_statements_1 (a int);
      CREATE TABLE test_multiple_statements_2 (a int);
      DROP TABLE test_multiple_statements_1;
      DROP TABLE test_multiple_statements_2;
    """

    resp = _make_query(self.client, hql, database=self.db_name)
    resp = wait_for_query_to_finish(self.client, resp, max=30.0)

    content = json.loads(resp.content)
    history_id = content['id']
    query_history = QueryHistory.get(id=history_id)

    resp = self.client.get("/beeswax/results/%s/0?format=json" % history_id)
    content = json.loads(resp.content)
    assert_equal('DROP TABLE test_multiple_statements_2', query_history.get_current_statement(), content)


  def test_multiple_statements_with_result_set(self):
    hql = """
      SELECT foo FROM test;
      SELECT count(*) FROM test;
    """

    resp = _make_query(self.client, hql, database=self.db_name)

    content = json.loads(resp.content)
    assert_true('watch_url' in content, content)
    watch_url = content['watch_url']
    assert_equal('SELECT foo FROM test', content.get('statement'), content)

    resp = wait_for_query_to_finish(self.client, resp, max=30.0)
    content = fetch_query_result_data(self.client, resp)

    assert_false(content.get('is_finished'), content)

    resp = self.client.post(watch_url, {'next': True})
    content = json.loads(resp.content)
    assert_equal('SELECT count(*) FROM test', content.get('statement'), content)


  def test_multiple_statements_various_queries(self):
    hql = """
      CREATE TABLE test_multiple_statements_2 (a int);
      DROP TABLE test_multiple_statements_2;
      SELECT foo FROM test;
    """

    resp = _make_query(self.client, hql, database=self.db_name)

    content = json.loads(resp.content)
    assert_equal('CREATE TABLE test_multiple_statements_2 (a int)', content.get('statement'), content)

    resp = wait_for_query_to_finish(self.client, resp, max=30.0)
    content = json.loads(resp.content)
    assert_equal('SELECT foo FROM test', content.get('statement'), content)

    content = fetch_query_result_data(self.client, resp)
    assert_true(content.get('is_finished'), content)


  def test_multiple_statements_with_next_button(self):
    hql = """
      show tables;
      select * from test
    """

    resp = _make_query(self.client, hql, database=self.db_name)

    # First statement
    content = json.loads(resp.content)
    watch_url = content['watch_url']
    assert_equal('show tables', content.get('statement'), content)

    resp = wait_for_query_to_finish(self.client, resp, max=30.0)
    content = fetch_query_result_data(self.client, resp)
    assert_true([u'test'] in content.get('results'), content)

    # Next statement
    resp = self.client.post(watch_url, {'next': True, 'query-query': hql})
    content = json.loads(resp.content)
    assert_equal('select * from test', content.get('statement'), content)

    resp = wait_for_query_to_finish(self.client, resp, max=30.0)
    content = fetch_query_result_data(self.client, resp)
    assert_true([0, u'0x0'] in content.get('results'), content)


  def test_multiple_statements_with_params(self):
    #@TODO@ Prakash fix this test
    raise SkipTest
    hql = """
      select ${x} from test;
      select ${y} from test;
    """

    resp = _make_query(self.client, hql, params=[('x', '1'), ('y', '2')], database=self.db_name)

    # First statement
    content = json.loads(resp.content)
    watch_url = content['watch_url']
    assert_equal('select ${x} from test', content.get('statement'), content)

    resp = wait_for_query_to_finish(self.client, resp, max=30.0)
    content = fetch_query_result_data(self.client, resp)

    # Next statement
    resp = self.client.post(watch_url, {'next': True, 'query-query': hql})
    content = json.loads(resp.content)
    assert_equal('select ${y} from test', content.get('statement'), content)

    resp = wait_for_query_to_finish(self.client, resp, max=30.0)


  def test_multiple_statements_with_error(self):
    hql = """
      show tables;
      select * from
    """

    resp = _make_query(self.client, hql, database=self.db_name)

    content = json.loads(resp.content)
    watch_url = content['watch_url']
    assert_equal('show tables', content.get('statement'), content)

    resp = wait_for_query_to_finish(self.client, resp, max=30.0)

    resp = self.client.post(watch_url, {'next': True, 'query-query': hql})
    content = json.loads(resp.content)
    assert_true('Error while compiling statement' in content.get('message'), content)

    hql = """
      show tables;
      select * from test
    """

    # Retry where we were with the statement fixed
    resp = self.client.post(watch_url, {'next': True, 'query-query': hql})
    content = json.loads(resp.content)
    assert_equal('select * from test', content.get('statement'), content)


  def test_parallel_queries(self):
    """
    Test that we can issue two queries to the BeeswaxServer in parallel.
    However, the test assertion has been plagued by the django test framework,
    which does not set request.context in a thread safe manner.

    So we check the results by looking at the csv files.
    """
    raise SkipTest # sqlite does not support concurrent transaction

    PARALLEL_TASKS = 2
    responses = [ None ] * PARALLEL_TASKS
    threads = []
    # Protects responses
    lock = threading.Lock()

    for i in range(PARALLEL_TASKS):
      t = threading.Thread(target=self._parallel_query_helper,
                           args=(i, responses, lock, PARALLEL_TASKS))
      t.start()
      threads.append(t)

    for t in threads:
      t.join()

    # Commit transactions to be sure that QueryHistory up to date
    transaction.commit()

    for i in range(PARALLEL_TASKS):
      csv = get_csv(self.client, responses[i])
      # We get 3 rows: Column header, and 2 rows of results in double quotes
      answer = [ int(data.strip('"')) for data in csv.split()[1:] ]
      assert_equal( [ i + 1, i + 2 ], answer)


  def test_data_export_limit_clause(self):
    limit = 3
    hql = 'SELECT foo FROM `%(db)s`.`test` limit %(limit)d' % {'limit': limit, 'db': self.db_name}
    query = hql_query(hql)

    handle = self.db.execute_and_wait(query)
    # Get the result in csv. Should have 3 + 1 header row.
    csv_resp = download(handle, 'csv', self.db)
    csv_content = ''.join(csv_resp.streaming_content)
    assert_equal(len(csv_content.strip().split('\n')), limit + 1)


  def test_query_done_cb(self):
    hql = 'SELECT * FROM `%(db)s`.`test`' % {'db': self.db_name}
    query = hql_query(hql)
    query._data_dict['query']['email_notify'] = False
    query_history = self.db.execute_and_watch(query)

    response = self.client.get('/beeswax/query_cb/done/%s' % query_history.server_id)
    assert_true('email_notify is false' in response.content, response.content)

    query = hql_query(hql)
    query._data_dict['query']['email_notify'] = True
    query_history = self.db.execute_and_watch(query)

    response = self.client.get('/beeswax/query_cb/done/%s' % query_history.server_id,)
    assert_true('sent' in response.content, response.content)

    response = self.client.get('/beeswax/query_cb/done/blahblahblah')
    assert_true('QueryHistory matching query does not exist' in response.content, response.content)


  def test_data_export(self):
    hql = 'SELECT * FROM `%(db)s`.`test`' % {'db': self.db_name}
    query = hql_query(hql)

    # Get the result in xls.
    handle = self.db.execute_and_wait(query)
    resp = download(handle, 'xls', self.db)

    sheet_data = _read_xls_sheet_data(resp)
    num_cols = len(sheet_data[0])
    # It should have 257 lines (256 + header)
    assert_equal(len(sheet_data), 257, sheet_data)

    # Get the result in csv.
    query = hql_query(hql)
    handle = self.db.execute_and_wait(query)

    resp = download(handle, 'csv', self.db)
    csv_resp = ''.join(resp.streaming_content)
    csv_data = [[int(col) if col.isdigit() else col for col in row.split(',')] for row in csv_resp.strip().split('\r\n')]

    assert_equal(sheet_data, csv_data)

    # Test max cell limit truncation
    finish = conf.DOWNLOAD_ROW_LIMIT.set_for_testing(5)
    try:
      hql = 'SELECT * FROM `%(db)s`.`test`' % {'db': self.db_name}
      query = hql_query(hql)
      handle = self.db.execute_and_wait(query)
      resp = download(handle, 'xls', self.db)
      sheet_data = _read_xls_sheet_data(resp)
      # It should have 6 lines (header + 5 lines)
      assert_equal(len(sheet_data), 6, sheet_data)
    finally:
      finish()

    finish = conf.DOWNLOAD_BYTES_LIMIT.set_for_testing(1024)
    try:
      hql = 'SELECT * FROM `%(db)s`.`test`' % {'db': self.db_name}
      query = hql_query(hql)
      handle = self.db.execute_and_wait(query)
      resp = download(handle, 'csv', self.db)
      content = "".join(resp.streaming_content)
      assert_true(len(content) <= 1024)
    finally:
      finish()


  def test_data_upload(self):
    hql = 'SELECT * FROM `%(db)s`.`test`' % {'db': self.db_name}
    query = hql_query(hql)

    handle = self.db.execute_and_wait(query)
    csv_file = self.cluster.fs_prefix + '/test_data_upload.csv'
    upload(csv_file, handle, self.user, self.db, self.cluster.fs)

    assert_true(self.cluster.fs.exists(csv_file))


  def test_designs(self):
    #@TODO@ Prakash fix this test
    raise SkipTest
    if is_live_cluster():
      raise SkipTest('HUE-2902: Skipping because test is not reentrant')

    cli = self.client

    # An auto hql design should be created, and it should ignore the given name and desc
    _make_query(self.client, 'SELECT bogus FROM test', name='mydesign', desc='hyatt', database=self.db_name)
    resp = cli.get('/beeswax/list_designs')
    n_designs = len(resp.context[0]['page'].object_list)

    # Retrieve that design. It's the first one since it's most recent
    design = beeswax.models.SavedQuery.objects.all()[0]
    resp = cli.get('/beeswax/execute/design/%s' % design.id)

    assert_true('query' in resp.context[0]._data, resp.context)
    assert_equal(design, resp.context[0]._data['design'], resp.context)

    # Retrieve that query history. It's the first one since it's most recent
    query_history = beeswax.models.QueryHistory.objects.all()[0]
    resp = cli.get('/beeswax/execute/query/%s' % query_history.id)
    assert_true('query' in resp.context[0]._data, resp.context)
    assert_true(resp.context[0]._data['query'] is not None, resp.context)
    assert_true('design' in resp.context[0]._data, resp.context)
    assert_true(resp.context[0]._data['design'] is not None, resp.context)

    resp = cli.get(reverse('beeswax:api_fetch_saved_design', kwargs={'design_id': design.id}))
    content = json.loads(resp.content)
    assert_true('SELECT bogus FROM test' in content['design']['query'], content)

    # Make a valid auto hql design
    resp = _make_query(self.client, 'SELECT * FROM test', database=self.db_name)
    wait_for_query_to_finish(self.client, resp, max=60.0)

    resp = cli.get('/beeswax/list_designs')
    nplus_designs = len(resp.context[0]._data['page'].object_list)
    assert_true(nplus_designs == n_designs, 'Auto design should not show up in list_designs')

    # Test explicit save and use another DB
    query = 'MORE BOGUS JUNKS FROM test'
    other_db = '%s_other' % self.db_name
    resp = _make_query(self.client, query, name='rubbish', submission_type='Save', database=other_db)
    content = json.loads(resp.content)
    assert_equal(0, content['status'])
    assert_true('design_id' in content, content)

    resp = cli.get('/beeswax/list_designs')
    assert_true('rubbish' in resp.content, resp.content)
    nplusplus_designs = len(resp.context[0]._data['page'].object_list)
    assert_true(nplusplus_designs > nplus_designs)

    # Retrieve that design and check correct DB is selected
    design = beeswax.models.SavedQuery.objects.filter(name='rubbish')[0]
    resp = cli.get(reverse('beeswax:api_fetch_saved_design', kwargs={'design_id': design.id}))
    content = json.loads(resp.content)
    assert_true(query in content['design']['query'], content)
    assert_equal('', content['design']['desc'], content)
    assert_equal(other_db, content['design']['database'], content)

    # Clone the rubbish design
    len_before = len(beeswax.models.SavedQuery.objects.filter(name__contains='rubbish'))
    resp = cli.get('/beeswax/clone_design/%s' % (design.id,))
    len_after = len(beeswax.models.SavedQuery.objects.filter(name__contains='rubbish'))
    assert_equal(len_before + 1, len_after)

    # Make 3 more designs
    resp = cli.get('/beeswax/clone_design/%s' % (design.id,))
    resp = cli.get('/beeswax/clone_design/%s' % (design.id,))
    resp = cli.get('/beeswax/clone_design/%s' % (design.id,))
    designs = beeswax.models.SavedQuery.objects.filter(name__contains='rubbish')[:3]

    # Delete a design
    resp = cli.get('/beeswax/delete_designs')
    assert_true('Delete design(s)' in resp.content, resp.content)
    resp = cli.post('/beeswax/delete_designs', {u'designs_selection': [design.id]})
    assert_equal(resp.status_code, 302)

    # Delete designs
    design_ids = list(map(str, designs.values_list('id', flat=True)))
    resp = cli.get('/beeswax/delete_designs', {u'designs_selection': design_ids})
    assert_true('Delete design(s)' in resp.content, resp.content)
    #@TODO@: Prakash fix this test
    #resp = cli.post('/beeswax/delete_designs', {u'designs_selection': design_ids})
    #assert_equal(resp.status_code, 302)

    # Helper to test the view, filtering, etc
    def do_view(param):
      resp = cli.get('/beeswax/list_designs?' + param)
      assert_true(len(resp.context[0]['page'].object_list) >= 0)     # Make the query run
      return resp

    do_view('user=test')
    do_view('text=whatever')
    do_view('type=hql')
    do_view('sort=date')
    do_view('sort=-date')
    do_view('sort=name')
    do_view('sort=-name')
    do_view('sort=desc')
    do_view('sort=-desc')
    do_view('sort=type')
    do_view('sort=-type')
    do_view('sort=name&user=bogus')
    resp = do_view('sort=-type&user=test&type=hql&text=Rubbish')
    assert_true('rubbish' in resp.content)

    # Test personal saved queries permissions
    client_me = make_logged_in_client(username='its_me', is_superuser=False, groupname='test')
    grant_access("its_me", "test", "beeswax")
    _make_query(client_me, "select one", name='client query 1', submission_type='Save')
    _make_query(client_me, "select two", name='client query 2', submission_type='Save')

    # TODO in HUE-1589
    raise SkipTest

    finish = conf.SHARE_SAVED_QUERIES.set_for_testing(True)
    try:
      resp = client_me.get('/beeswax/list_designs')
      assert_true('client query 1' in resp.content, resp.content)
      assert_true('client query 2' in resp.content, resp.content)
    finally:
      finish()

    finish = conf.SHARE_SAVED_QUERIES.set_for_testing(False)
    try:
      resp = client_me.get('/beeswax/list_designs')
      assert_true('client query 1' in resp.content)
      assert_true('client query 2' in resp.content)
    finally:
      finish()
      client_me.logout()

    # Login as someone else
    client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test')
    grant_access("not_me", "test", "beeswax")
    finish = conf.SHARE_SAVED_QUERIES.set_for_testing(True)
    try:
      resp = client_not_me.get('/beeswax/list_designs')
      assert_true('client query 1' in resp.content)
      assert_true('client query 2' in resp.content)
    finally:
      finish()

    finish = conf.SHARE_SAVED_QUERIES.set_for_testing(False)
    try:
      resp = client_not_me.get('/beeswax/list_designs')
      assert_true('client query 1' not in resp.content)
      assert_true('client query 2' not in resp.content)
    finally:
      finish()
      client_not_me.logout()

    # Login as super user
    client_admin = make_logged_in_client('admin', is_superuser=True)
    finish = conf.SHARE_SAVED_QUERIES.set_for_testing(True)
    try:
      resp = client_admin.get('/beeswax/list_designs')
      assert_true('client query 1' in resp.content)
      assert_true('client query 2' in resp.content)
    finally:
      finish()

    finish = conf.SHARE_SAVED_QUERIES.set_for_testing(False)
    try:
      resp = client_admin.get('/beeswax/list_designs')
      assert_true('client query 1' in resp.content)
      assert_true('client query 2' in resp.content)
    finally:
      finish()
      client_admin.logout()


  def test_my_queries(self):
    # Explicit save a design
    _make_query(self.client, "select noHQL", name='my rubbish kuery', submission_type='Save', database=self.db_name)
    # Run something
    _make_query(self.client, "Even More Bogus Junk", database=self.db_name)
    resp = self.client.get('/beeswax/my_queries')
    assert_true('my rubbish kuery' in resp.content, resp.content)
    assert_true('Even More Bogus Junk' in resp.content)

    # Login as someone else
    client_not_me = make_logged_in_client('not_me', groupname='test')
    grant_access("not_me", "test", "beeswax")

    resp = client_not_me.get('/beeswax/my_queries')
    assert_true('my rubbish kuery' not in resp.content)
    assert_true('Even More Bogus Junk' not in resp.content)
    client_not_me.logout()


  def test_save_results_to_dir(self):

    def save_and_verify(select_resp, target_dir, verify=True):
      content = json.loads(select_resp.content)
      qid = content['id']
      save_data = {
        'type': 'hdfs-directory',
        'path': target_dir
      }
      resp = self.client.post('/beeswax/api/query/%s/results/save/hdfs/directory' % qid, save_data, follow=True)
      content = json.loads(resp.content)

      if content['status'] == 0:
        success_url = content['success_url']
        resp = self.client.get(content['watch_url'], follow=True)
        resp = wait_for_query_to_finish(self.client, resp, max=120)
        resp.success_url = success_url # Hack until better API

      # Check that data is right
      if verify:
        target_ls = _list_dir_without_temp_files(self.cluster.fs, target_dir)
        assert_equal(len(target_ls), 1)
        data_buf = ""

        for target in target_ls:
          target_file = self.cluster.fs.open(target_dir + '/' + target)
          data_buf += target_file.read()
          target_file.close()

        assert_equal(256, len(data_buf.strip().split('\n')))
        assert_true('255' in data_buf)

      return resp

    TARGET_DIR_ROOT = self.cluster.fs_prefix + '/beeswax.test_save_directory_results'

    # Already existing dir
    if not self.cluster.fs.exists(TARGET_DIR_ROOT):
      self.cluster.fs.mkdir(TARGET_DIR_ROOT)
      self.cluster.fs.chown(TARGET_DIR_ROOT, user='test')
    hql = "SELECT * FROM test"
    resp = _make_query(self.client, hql, wait=True, local=False, max=180.0, database=self.db_name)
    resp = save_and_verify(resp, TARGET_DIR_ROOT, verify=False)
    assert_true('Directory already exists' in resp.content, resp.content)

    # SELECT *. (Result dir is same as table dir.)
    hql = "SELECT * FROM test"
    resp = _make_query(self.client, hql, wait=True, local=False, max=180.0, database=self.db_name)
    resp = save_and_verify(resp, TARGET_DIR_ROOT + '/1', verify=False)
    resp = self.client.get(resp.success_url)
    # Success and went to FB
    assert_true('File Browser' in resp.content, resp.content)

    # SELECT columns. (Result dir is in /tmp.)
    hql = "SELECT foo, bar FROM test"
    resp = _make_query(self.client, hql, wait=True, local=False, max=180.0, database=self.db_name)
    resp = save_and_verify(resp, TARGET_DIR_ROOT + '/2')
    resp = self.client.get(resp.success_url)
    assert_true('File Browser' in resp.content, resp.content)

    # Partition tables
    hql = "SELECT * FROM test_partitions"
    resp = _make_query(self.client, hql, wait=True, local=False, max=180.0, database=self.db_name)
    resp = save_and_verify(resp, TARGET_DIR_ROOT + '/3', verify=False)
    resp = self.client.get(resp.success_url)
    assert_true('File Browser' in resp.content, resp.content)


  def test_save_results_to_file(self):

    def save_and_verify(select_resp, target_file, overwrite=True, verify=True):
      content = json.loads(select_resp.content)
      qid = content['id']
      save_data = {
        'type': 'hdfs',
        'path': target_file,
        'overwrite': overwrite
      }
      resp = self.client.post('/beeswax/api/query/%s/results/save/hdfs/file' % qid, save_data, follow=True)
      content = json.loads(resp.content)

      if content['status'] == 0:
        success_url = content['success_url']
        resp = self.client.get(content['watch_url'], follow=True)
        resp = wait_for_query_to_finish(self.client, resp, max=60)
        resp.success_url = success_url # Hack until better API

      # Check that data is right
      if verify:
        assert_true(self.cluster.fs.exists(target_file))
        assert_true(self.cluster.fs.isfile(target_file))
        data_buf = ""

        _file = self.cluster.fs.open(target_file)
        data_buf += _file.read()
        _file.close()

        assert_equal(256, len(data_buf.strip().split('\n')))
        assert_true('255' in data_buf)

      return resp

    TARGET_FILE = self.cluster.fs_prefix + '/beeswax.test_save_file_results'
    if self.cluster.fs.exists(TARGET_FILE):
      self.cluster.fs.rmtree(TARGET_FILE)

    # SELECT columns. (Result dir is in /tmp.)
    hql = "SELECT foo, bar FROM test"
    resp = _make_query(self.client, hql, wait=True, local=False, max=180.0, database=self.db_name)
    resp = save_and_verify(resp, TARGET_FILE)
    resp = self.client.get(resp.success_url)
    assert_true('File Browser' in resp.content, resp.content)

    # overwrite = false
    hql = "SELECT foo, bar FROM test"
    resp = _make_query(self.client, hql, wait=True, local=False, max=180.0, database=self.db_name)
    resp = save_and_verify(resp, TARGET_FILE, overwrite=False, verify=False)
    assert_true('-3' in resp.content, resp.content)
    assert_true('already exists' in resp.content)

    # Partition tables
    hql = "SELECT * FROM test_partitions"
    resp = _make_query(self.client, hql, wait=True, local=False, max=180.0, database=self.db_name)
    resp = save_and_verify(resp, TARGET_FILE, verify=False)
    resp = self.client.get(resp.success_url)
    assert_true('File Browser' in resp.content, resp.content)


  def test_save_results_to_tbl(self):

    def save_and_verify(select_resp, target_tbl):
      """Check that saving to table works"""
      content = json.loads(select_resp.content)
      qid = content['id']
      save_data = {
        'type': 'hive-table',
        'table': target_tbl
      }
      resp = self.client.post('/beeswax/api/query/%s/results/save/hive/table' % qid, save_data, follow=True)
      content = json.loads(resp.content)
      resp = self.client.get(content['watch_url'], follow=True)
      wait_for_query_to_finish(self.client, resp, max=120)

      # Check that data is right. The SELECT may not give us the whole table.
      resp = _make_query(self.client, 'SELECT * FROM %s' % target_tbl, wait=True, local=False, database=self.db_name)
      content = fetch_query_result_data(self.client, resp)
      for i in range(90):
        assert_equal([i, '0x%x' % (i,)], content['results'][i])

    TARGET_TBL_ROOT = 'test_copy'

    # SELECT *. (Result dir is same as table dir.)
    hql = "SELECT * FROM test"
    resp = _make_query(self.client, hql, wait=True, local=False, max=180.0, database=self.db_name)
    save_and_verify(resp, TARGET_TBL_ROOT + '_1')

    # SELECT columns. (Result dir is in /tmp.)
    hql = "SELECT foo, bar FROM test"
    resp = _make_query(self.client, hql, wait=True, local=False, max=180.0, database=self.db_name)
    save_and_verify(resp, TARGET_TBL_ROOT + '_2')

    # Save to another DB
    hql = "SELECT * FROM test"
    resp = _make_query(self.client, hql, wait=True, local=False, max=180.0, database=self.db_name)
    other_db = '%s_other' % self.db_name
    save_and_verify(resp, other_db + '.' + TARGET_TBL_ROOT)


  def test_install_examples(self):
    assert_true(not beeswax.models.MetaInstall.get().installed_example)

    # Check popup
    resp = self.client.get('/beeswax/install_examples')
    assert_true('POST request is required.' in json.loads(resp.content)['message'])

    self.client.post('/beeswax/install_examples', {'db_name': self.db_name})

    # New tables exists
    resp = self.client.get('/metastore/tables/%s?format=json' % self.db_name)
    data = json.loads(resp.content)
    assert_true('sample_08' in data['table_names'])
    assert_true('sample_07' in data['table_names'])
    assert_true('customers' in data['table_names'])

    # Sample tables contain data (examples are installed in db_name DB)
    resp = self.client.get(reverse('beeswax:get_sample_data', kwargs={'database': self.db_name, 'table': 'sample_07'}))
    data = json.loads(resp.content)
    assert_true(data['rows'], data)
    resp = self.client.get(reverse('beeswax:get_sample_data', kwargs={'database': self.db_name, 'table': 'sample_08'}))
    data = json.loads(resp.content)
    assert_true(data['rows'], data)
    resp = self.client.get(reverse('beeswax:get_sample_data', kwargs={'database': self.db_name, 'table': 'customers'}))

    if USE_NEW_EDITOR.get():
      # New queries exist
      resp = self.client.get('/desktop/api2/docs/')
      data = json.loads(resp.content)
      doc_names = [doc['name'] for doc in data['documents']]
      assert_true('examples' in doc_names, data)
      uuid = next((doc['uuid'] for doc in data['documents'] if doc['name'] == 'examples'), None)

      resp = self.client.get('/desktop/api2/doc/', {'uuid': uuid})
      data = json.loads(resp.content)
      doc_names = [doc['name'] for doc in data['children']]
      assert_true('Sample: Job loss' in doc_names, data)
      assert_true('Sample: Salary growth' in doc_names, data)
      assert_true('Sample: Top salary' in doc_names, data)
      assert_true('Sample: Customers' in doc_names, data)
    else:
      # New designs exists
      resp = self.client.get('/beeswax/list_designs')
      assert_true('Sample: Job loss' in resp.content, resp.content)
      assert_true('Sample: Salary growth' in resp.content)
      assert_true('Sample: Top salary' in resp.content)
      assert_true('Sample: Customers' in resp.content)

      # Now install it a second time, and no error
      resp = self.client.post('/beeswax/install_examples', {'db_name': self.db_name})
      assert_equal(0, json.loads(resp.content)['status'])
      assert_equal('', json.loads(resp.content)['message'])


  def test_create_table_generation(self):
    """
    Checks HQL generation for create table.

    NOT TESTED/DONE: Validation checks for the inputs.
    """
    # Make sure we get a form
    resp = self.client.get("/beeswax/create/create_table/%s" % self.db_name)
    assert_true("Field terminator" in resp.content)
    # Make a submission
    resp = self.client.post("/beeswax/create/create_table/%s" % self.db_name, {
      'table-name': 'my_table',
      'table-comment': 'Yo>>>>dude',  # Make sure escaping is sort of ok.
      'table-row_format': 'Delimited',
      'table-field_terminator_0': r',',
      'table-collection_terminator_0': r'\002',
      'table-map_key_terminator_0': r'\003',
      'table-file_format': 'TextFile',
      'table-use_default_location': 'False',
      'table-skip_header': 'False',
      'table-external_location': '/tmp/foo',
      'columns-0-column_name': 'my_col',
      'columns-0-column_type': 'string',
      'columns-0-_exists': 'True',
      'columns-next_form_id': '1',
      'partitions-next_form_id': '0',
      'create': 'Create table',
    }, follow=True)

    # Ensure we can see table.
    response = self.client.post("/metastore/table/%s/my_table?format=json" % self.db_name, {'format': 'json'})
    data = json.loads(response.content)
    assert_true("my_col" in [col['name'] for col in data['cols']], data)


  def test_create_table_timestamp(self):
    # Check form
    response = self.client.get('/beeswax/create/create_table/%s' % self.db_name)
    assert_true('<option value="timestamp">timestamp</option>' in response.content, response.content)

    # Check creation
    filename = self.cluster.fs_prefix + '/timestamp_data'

    # Bad format
    self._make_custom_data_file(filename, [0, 0, 0])
    self._make_table('timestamp_invalid_data', 'CREATE TABLE timestamp_invalid_data (timestamp1 TIMESTAMP)', filename)

    resp = self.client.get(reverse('beeswax:get_sample_data', kwargs={'database': self.db_name, 'table': 'timestamp_invalid_data'}))
    rows = json.loads(resp.content)['rows']
    flat_rows = sum(rows, [])
    assert_true("NULL" in flat_rows, flat_rows)

    # Good format
    self._make_custom_data_file(filename, ['2012-01-01 10:11:30', '2012-01-01 10:11:31'])
    self._make_table('timestamp_valid_data', 'CREATE TABLE timestamp_valid_data (timestamp1 TIMESTAMP)', filename)

    resp = self.client.get(reverse('beeswax:get_sample_data', kwargs={'database': self.db_name, 'table': 'timestamp_valid_data'}))
    rows = json.loads(resp.content)['rows']
    flat_rows = sum(rows, [])
    assert_true("2012-01-01 10:11:30.0" in flat_rows, flat_rows)


  def test_partitioned_create_table(self):
    # Make sure we get a form
    resp = self.client.get("/beeswax/create/create_table/%s" % self.db_name)
    assert_true("Field terminator" in resp.content)
    # Make a submission
    resp = self.client.post("/beeswax/create/create_table/%s" % self.db_name, {
      'table-name': 'my_table2',
      'table-row_format': 'Delimited',
      'table-field_terminator_0': r'\001',
      'table-collection_terminator_0': r'\002',
      'table-map_key_terminator_0': r'\003',
      'table-file_format': 'TextFile',
      'table-use_default_location': 'True',
      'table-skip_header': 'False',
      'columns-0-column_name': 'my_col',
      'columns-0-column_type': 'string',
      'columns-0-_exists': 'True',
      'columns-next_form_id': '1',
      'partitions-0-column_name': 'my_partition',
      'partitions-0-column_type': 'string',
      'partitions-0-_exists': 'True',
      'partitions-next_form_id': '1',
      'create': 'Create table',
    }, follow=True)

    history = QueryHistory.objects.latest('id')

    assert_equal_mod_whitespace("""
        CREATE TABLE `%s.my_table2`
        (
         `my_col` string
        )
        PARTITIONED BY
        (
          `my_partition` string
        )
        ROW FORMAT DELIMITED
          FIELDS TERMINATED BY '\\001'
          COLLECTION ITEMS TERMINATED BY '\\002'
          MAP KEYS TERMINATED BY '\\003'
          STORED AS TextFile
    """ % self.db_name, history.query)


  def test_create_table_dependencies(self):
    """
    Test field dependency in the create table form
    """
    resp = self.client.post("/beeswax/create/create_table/%s" % self.db_name, {
      'table-name': 'my_table',
      'table-row_format': 'SerDe',
      # Missing SerDe fields!
      'table-file_format': 'InputFormat',
      # Input format fields missing!
      'columns-0-column_name': 'my_col',
      'columns-0-column_type': 'map',
      # Map key value missing!
      'columns-0-_exists': 'True',
      'columns-1-column_name': 'my_partition',
      'columns-1-column_type': 'string',
      'columns-1-is_partition_key': 'on',
      'columns-1-_exists': 'True',
      'columns-next_form_id': '2',
      'partitions-next_form_id': '0',
      'create': 'Create table',
    })

    # All of these errors should have been triggered!
    assert_true(resp.context[0]["table_form"].errors["input_format_class"])
    assert_true(resp.context[0]["table_form"].errors["output_format_class"])
    assert_true(resp.context[0]["table_form"].errors["serde_name"])
    assert_true(resp.context[0]["table_form"].errors["serde_properties"])
    assert_true(resp.context[0]["table_form"].errors["serde_properties"])

    assert_true(resp.context[0]["columns_form"].forms[0].errors["map_key_type"])
    assert_true(resp.context[0]["columns_form"].forms[0].errors["map_value_type"])


  def test_create_table_import(self):
    RAW_FIELDS = [
      ['ta\tb', 'nada', 'sp ace'],
      ['f\too', 'bar', 'fred'],
      ['a\ta', 'bb', 'cc'],
    ]
    CSV_FIELDS = [
      ['a', 'b', 'c'],
      ['"a,a"', '"b,b"', '"c,c"'],
      ['"a,\"\"a"', '"b,\"\"b"', '"c,\"\"c"'],
    ]

    def write_file(filename, raw_fields, delim, do_gzip=False):
      lines = [ delim.join(row) for row in raw_fields ]
      data = '\n'.join(lines)
      if do_gzip:
        sio = string_io()
        gzdat = gzip.GzipFile(fileobj=sio, mode='wb')
        gzdat.write(data)
        gzdat.close()
        data = sio.getvalue()

      f = self.cluster.fs.open(filename, "w")
      f.write(data)
      f.close()
      #self.cluster.fs.do_as_superuser(self.cluster.fs.chown, filename, 'test', 'test')

    #self.cluster.fs.do_as_user('test', self.cluster.fs.create_home_dir, '/user/test')

    write_file(self.cluster.fs_prefix + '/spacé.dat'.decode('utf-8'), RAW_FIELDS, ' ')
    write_file(self.cluster.fs_prefix + '/tab.dat', RAW_FIELDS, '\t')
    write_file(self.cluster.fs_prefix + '/comma.dat', RAW_FIELDS, ',')
    write_file(self.cluster.fs_prefix + '/pipes.dat', RAW_FIELDS, '|')
    write_file(self.cluster.fs_prefix + '/comma.dat.gz', RAW_FIELDS, ',', do_gzip=True)
    write_file(self.cluster.fs_prefix + '/comma.csv', CSV_FIELDS, ',')

    # Test auto delim selection
    resp = self.client.post('/beeswax/create/import_wizard/%s' % self.db_name, {
      'submit_file': 'on',
      'path': self.cluster.fs_prefix + '/comma.dat',
      'load_data': 'IMPORT',
      'name': 'test_create_import',
    })
    assert_equal(resp.context[0]['fields_list'], RAW_FIELDS)

    # Test same with gzip
    resp = self.client.post('/beeswax/create/import_wizard/%s' % self.db_name, {
      'submit_file': 'on',
      'path': self.cluster.fs_prefix + '/comma.dat.gz',
      'load_data': 'IMPORT',
      'name': 'test_create_import',
    })
    assert_equal(resp.context[0]['fields_list'], RAW_FIELDS)

    # Make sure space works
    resp = self.client.post('/beeswax/create/import_wizard/%s' % self.db_name, {
      'submit_preview': 'on',
      'path': self.cluster.fs_prefix + '/spacé.dat',
      'load_data': 'IMPORT',
      'name': 'test_create_import',
      'delimiter_0': ' ',
      'delimiter_1': '',
      'file_type': 'text',
    })
    assert_equal(len(resp.context[0]['fields_list'][0]), 4)

    # Make sure custom delimiters work
    resp = self.client.post('/beeswax/create/import_wizard/%s' % self.db_name, {
      'submit_preview': 'on',
      'path': self.cluster.fs_prefix + '/pipes.dat',
      'load_data': 'IMPORT',
      'name': 'test_create_import',
      'delimiter_0': '__other__',
      'delimiter_1': '|',
      'file_type': 'text',
    })
    assert_equal(len(resp.context[0]['fields_list'][0]), 3)

    # Make sure quoted CSV works
    resp = self.client.post('/beeswax/create/import_wizard/%s' % self.db_name, {
      'submit_preview': 'on',
      'path': self.cluster.fs_prefix + '/comma.csv',
      'load_data': 'IMPORT',
      'name': 'test_create_import_csv',
      'delimiter_0': '__other__',
      'delimiter_1': ',',
      'file_type': 'text',
    })
    assert_equal(resp.context[0]['fields_list'], [
      ['a', 'b', 'c'],
      ['a,a', 'b,b', 'c,c'],
      ['a,"a', 'b,"b', 'c,"c'],
    ] )

    # Test column definition
    resp = self.client.post('/beeswax/create/import_wizard/%s' % self.db_name, {
      'submit_delim': 'on',
      'path': self.cluster.fs_prefix + '/comma.dat.gz',
      'load_data': 'IMPORT',
      'name': 'test_create_import',
      'delimiter_0': ',',
      'delimiter_1': '',
      'file_type': 'gzip',
    })
    # Should have 3 columns available
    assert_equal(len(resp.context[0]['column_formset'].forms), 3)

    # Test table creation and data loading
    resp = self.client.post('/beeswax/create/import_wizard/%s' % self.db_name, {
      'submit_create': 'on',
      'path': self.cluster.fs_prefix + '/comma.dat.gz',
      'load_data': 'IMPORT',
      'name': 'test_create_import',
      'delimiter_0': ',',
      'delimiter_1': '',
      'file_type': 'gzip',
      'cols-0-_exists': 'True',
      'cols-0-column_name': 'col_a',
      'cols-0-column_type': 'string',
      'cols-1-_exists': 'True',
      'cols-1-column_name': 'col_b',
      'cols-1-column_type': 'string',
      'cols-2-_exists': 'True',
      'cols-2-column_name': 'col_c',
      'cols-2-column_type': 'string',
      'cols-next_form_id': '3',
    }, follow=True)

    #
    # Little nightmare here:
    # We have a POST (create table) with a redirect (load data) of redirect (show table)
    #
    assert_equal(resp.context[0]['action'], 'watch-redirect')
    on_success_url_load_data = resp.context[0]['on_success_url']
    assert_true('auto_load' in on_success_url_load_data, on_success_url_load_data)
    query_history = resp.context[0]['query_history']

    resp = self.client.get(reverse('beeswax:api_fetch_query_history', kwargs={'query_history_id': query_history.id}), follow=True)
    content = json.loads(resp.content)
    watch_url = content['query_history']['watch_url']

    class MockResponse(object):
      def __init__(self, content):
        self.content = json.dumps(content)

    # Wait for CREATE TABLE to finis
    resp = wait_for_query_to_finish(self.client, MockResponse({'status': 'ok', 'watch_url': watch_url}), max=180.0)

    # Get URL that will load the data into the table. Also get the URL that will show the table in metastore app.
    resp = self.client.get(on_success_url_load_data, follow=True)
    assert_equal(resp.context[0]['action'], 'watch-redirect')
    on_success_url_show_table = resp.context[0]['on_success_url']
    assert_true('/metastore/table/' in on_success_url_show_table, on_success_url_show_table)
    query_history = resp.context[0]['query_history']

    # Wait for load data to finish
    resp = wait_for_query_to_finish(self.client, MockResponse({'status': 'ok', 'watch_url': watch_url}), max=180.0)

    # Check data is in the table (by describing it)
    resp = self.client.get(on_success_url_show_table)
    cols = resp.context[0]['table'].cols
    assert_equal(len(cols), 3)
    assert_equal([ col.name for col in cols ], [ 'col_a', 'col_b', 'col_c' ])
    resp = self.client.get(reverse('beeswax:get_sample_data', kwargs={'database': self.db_name, 'table': 'test_create_import'}))
    rows = json.loads(resp.content)['rows']
    flat_rows = sum(rows, [])
    assert_true("nada" in flat_rows, flat_rows)
    assert_true("sp ace" in flat_rows, flat_rows)

    # Test table creation and data loading and removing header
    resp = self.client.post('/beeswax/create/import_wizard/%s' % self.db_name, {
      'submit_create': 'on',
      'path': self.cluster.fs_prefix + '/comma.csv',
      'load_data': 'IMPORT',
      'name': 'test_create_import_with_header',
      'delimiter_0': ',',
      'delimiter_1': '',
      'file_type': 'text',
      'cols-0-_exists': 'True',
      'cols-0-column_name': 'col_a',
      'cols-0-column_type': 'string',
      'cols-1-_exists': 'True',
      'cols-1-column_name': 'col_b',
      'cols-1-column_type': 'string',
      'cols-2-_exists': 'True',
      'cols-2-column_name': 'col_c',
      'cols-2-column_type': 'string',
      'cols-next_form_id': '3',
      'removeHeader': 'on'
    }, follow=True)

    # We have a POST (create table) with a redirect (load data) of redirect (show table)
    assert_equal(resp.context[0]['action'], 'watch-redirect')
    on_success_url_load_data = resp.context[0]['on_success_url']
    assert_true('auto_load' in on_success_url_load_data, on_success_url_load_data)
    query_history = resp.context[0]['query_history']

    resp = self.client.get(reverse('beeswax:api_fetch_query_history', kwargs={'query_history_id': query_history.id}), follow=True)
    content = json.loads(resp.content)
    watch_url = content['query_history']['watch_url']

    # Wait for CREATE TABLE to finis
    resp = wait_for_query_to_finish(self.client, MockResponse({'status': 'ok', 'watch_url': watch_url}), max=180.0)

    # Get URL that will load the data into the table. Also get the URL that will show the table in metastore app.
    resp = self.client.get(on_success_url_load_data, follow=True)
    assert_equal(resp.context[0]['action'], 'watch-redirect')
    on_success_url_show_table = resp.context[0]['on_success_url']
    assert_true('/metastore/table/' in on_success_url_show_table, on_success_url_show_table)
    query_history = resp.context[0]['query_history']

    # Wait for load data to finish
    resp = wait_for_query_to_finish(self.client, MockResponse({'status': 'ok', 'watch_url': watch_url}), max=180.0)

    # Check data is in the table (by describing it)
    resp = self.client.get(on_success_url_show_table)

    # Check data is in the table (by describing it)
    cols = resp.context[0]['table'].cols
    assert_equal(len(cols), 3)
    assert_equal([col.name for col in cols], ['col_a', 'col_b', 'col_c'])

    resp = self.client.get(reverse('beeswax:get_sample_data', kwargs={'database': self.db_name, 'table': 'test_create_import_with_header'}))
    rows = json.loads(resp.content)['rows']
    assert_equal([
      ['a', 'b', 'c'], # Gone as told to be header
      ['"a', 'a"', '"b'], # Hive does not support natively quoted CSV
      ['"a', '""a"', '"b']
    ], rows)


  def test_select_invalid_data(self):
    filename = self.cluster.fs_prefix + '/test_select_invalid_data'
    self._make_custom_data_file(filename, [1, 2, 3, 'NaN', 'INF', '-INF', 'BAD']) # Infinity not supported yet
    self._make_table('test_select_invalid_data', 'CREATE TABLE test_select_invalid_data (timestamp1 DOUBLE)', filename)

    hql = """
      SELECT * FROM test_select_invalid_data;
    """
    resp = _make_query(self.client, hql, database=self.db_name)
    resp = wait_for_query_to_finish(self.client, resp, max=30.0)

    content = json.loads(resp.content)
    history_id = content['id']
    query_history = QueryHistory.get(id=history_id)

    resp = self.client.get("/beeswax/results/%s/0?format=json" % history_id)
    content = json.loads(resp.content)
    assert_equal([[1.0], [2.0], [3.0], [u'NaN'], [u'NULL'], [u'NULL'], [u'NULL']], content['results'])


  def test_create_database(self):
    db_name = self.db_name + '_my_db'
    db_name_accent = self.db_name + '_credito'
    try:
      resp = self.client.post("/beeswax/create/database", {
        'name': db_name,
        'comment': 'foo',
        'create': 'Create database',
        'use_default_location': True,
      }, follow=True)
      resp = self.client.get(reverse("beeswax:api_watch_query_refresh_json", kwargs={'id': resp.context[0]['query'].id}), follow=True)
      resp = wait_for_query_to_finish(self.client, resp, max=180.0)
      resp = self.client.get("/metastore/databases/")
      assert_true(db_name in resp.context[0]["databases"], resp)

      # Test for accented characters in 'comment'
      resp = self.client.post("/beeswax/create/database", {
        'name': db_name_accent,
        'comment': 'crédito',
        'create': 'Create database',
        'use_default_location': True,
      }, follow=True)
      resp = self.client.get(reverse("beeswax:api_watch_query_refresh_json", kwargs={'id': resp.context[0]['query'].id}), follow=True)
      resp = wait_for_query_to_finish(self.client, resp, max=180.0)
      resp = self.client.get("/metastore/databases/")
      assert_true(db_name_accent in resp.context[0]['databases'], resp)
    finally:
      make_query(self.client, 'DROP DATABASE IF EXISTS %(db)s' % {'db': db_name}, wait=True)
      make_query(self.client, 'DROP DATABASE IF EXISTS %(db)s' % {'db': db_name_accent}, wait=True)


  def test_select_query_server(self):
    c = make_logged_in_client()
    _make_query(c, 'SELECT bogus FROM test', database=self.db_name) # Improvement: mock another server

    history = beeswax.models.QueryHistory.objects.latest('id')
    assert_equal('beeswax', history.server_name)
    assert_equal(HIVE_SERVER_HOST.get(), history.server_host)

    query_server = history.get_query_server_config()
    assert_equal('beeswax', query_server['server_name'])

    # NOTE: The history server is typically on a different server when live
    # cluster testing.
    if not is_live_cluster():
      assert_equal(get_localhost_name(), query_server['server_host'])

    assert_equal('hiveserver2', query_server['server_type'])
    assert_true(query_server['principal'] is None, query_server['principal']) # No default hive/HOST_@TEST.COM so far


  def test_select_multi_db(self):
    response = _make_query(self.client, 'SELECT * FROM test LIMIT 5', local=False, database=self.db_name)
    response = wait_for_query_to_finish(self.client, response)
    content = fetch_query_result_data(self.client, response)
    assert_true([0, u'0x0'] in content['results'], content)

    response = _make_query(self.client, 'SHOW TABLES', local=False, database='%s_other' % self.db_name)
    response = wait_for_query_to_finish(self.client, response)
    content = fetch_query_result_data(self.client, response)
    assert_true('tab_name' in content['columns'][0]['name'], content)

    response = _make_query(self.client, 'SELECT * FROM test LIMIT 5', local=False, database='not_there')
    content = json.loads(response.content)
    assert_equal(-1, content.get('status'), content)


  def test_list_design_pagination(self):
    client = make_logged_in_client()

    _make_query(client, 'SELECT', name='my query history', submission_type='Save', database=self.db_name)
    design = SavedQuery.objects.get(name='my query history')

    for i in range(25):
      client.get('/beeswax/clone_design/%s' % (design.id,))

    resp = client.get('/beeswax/list_designs')
    ids_page_1 = set([query.id for query in resp.context[0]['page'].object_list])
    resp = client.get('/beeswax/list_designs?q-page=2')
    if resp.context[0]['page']:
      ids_page_2 = set([query.id for query in resp.context[0]['page'].object_list])
    else:
      ids_page_2 = set([])
    for id in ids_page_2:
      assert_true(id not in ids_page_1)

    SavedQuery.objects.filter(name='my query history').delete()


  def test_get_table_sample(self):
    client = make_logged_in_client()

    resp = client.get(reverse('beeswax:get_sample_data', kwargs={'database': self.db_name, 'table': 'test'}))
    json_resp = json.loads(resp.content)
    assert_equal(0, json_resp['status'], json_resp)
    assert_true('test.foo' in json_resp['headers'], json_resp)
    assert_true([0, '0x0'] in json_resp['rows'], json_resp)


  def test_get_sample_partitioned(self):
    # Test limit of one partition
    finish = conf.QUERY_PARTITIONS_LIMIT.set_for_testing(1)
    try:
      table_name = 'test_partitions'
      partition_spec = "(`baz`='baz_one' AND `boom`=12345)"
      table = self.db.get_table(database=self.db_name, table_name=table_name)
      hql = self.db._get_sample_partition_query(self.db_name, table, limit=10)
      assert_equal(hql, 'SELECT * FROM `%s`.`%s` WHERE %s LIMIT 10' % (self.db_name, table_name, partition_spec))
    finally:
      finish()

    # Test limit of more than one partition
    finish = conf.QUERY_PARTITIONS_LIMIT.set_for_testing(2)
    try:
      table_name = 'test_partitions'
      partition_spec = "(`baz`='baz_one' AND `boom`=12345) OR (`baz`='baz_foo' AND `boom`=67890)"
      table = self.db.get_table(database=self.db_name, table_name=table_name)
      hql = self.db._get_sample_partition_query(self.db_name, table, limit=10)
      assert_equal(hql, 'SELECT * FROM `%s`.`%s` WHERE %s LIMIT 10' % (self.db_name, table_name, partition_spec))
    finally:
      finish()

    # Test table with non-STRING (INT) partition columns
    # Also tests for single partition column case
    hql = """
      CREATE TABLE test_partitions_int (a INT) PARTITIONED BY (b INT);
      INSERT OVERWRITE TABLE test_partitions_int PARTITION (b=100)
        SELECT 101 AS a FROM test_partitions LIMIT 1;
      INSERT OVERWRITE TABLE test_partitions_int PARTITION (b=200)
        SELECT 201 AS a FROM test_partitions LIMIT 1;
      INSERT OVERWRITE TABLE test_partitions_int PARTITION (b=300)
        SELECT 301 AS a FROM test_partitions LIMIT 1;
    """
    resp = _make_query(self.client, hql, wait=True, local=False, max=180.0, database=self.db_name)

    finish = conf.QUERY_PARTITIONS_LIMIT.set_for_testing(2)
    try:
      table_name = 'test_partitions_int'
      table = self.db.get_table(database=self.db_name, table_name=table_name)
      result = self.db.get_sample(self.db_name, table)
      sample = list(result.rows())
      assert_equal(len(sample), 2, sample)
    finally:
      finish()

    # Test table that is partitioned but empty
    hql = """
      CREATE TABLE test_partitions_empty (a STRING) PARTITIONED BY (b STRING);
    """
    resp = _make_query(self.client, hql, wait=True, local=False, max=60.0, database=self.db_name)

    finish = conf.QUERY_PARTITIONS_LIMIT.set_for_testing(2)
    try:
      table_name = 'test_partitions_empty'
      table = self.db.get_table(database=self.db_name, table_name=table_name)
      result = self.db.get_sample(self.db_name, table)
      sample = list(result.rows())
      assert_equal(len(sample), 0, sample)
    finally:
      finish()


  def test_redacting_queries(self):
    c = make_logged_in_client()

    old_policies = redaction.global_redaction_engine.policies
    redaction.global_redaction_engine.policies = [
      RedactionPolicy([
        RedactionRule('', 'ssn=\d{3}-\d{2}-\d{4}', 'ssn=XXX-XX-XXXX'),
      ])
    ]

    logfilter.add_log_redaction_filter_to_logger(redaction.global_redaction_engine, logging.root)

    try:
      # Make sure redacted queries are redacted.
      query = 'SELECT "ssn=123-45-6789"'
      expected_query = 'SELECT "ssn=XXX-XX-XXXX"'

      resp = make_query(c, query, database=self.db_name)
      content = json.loads(resp.content)
      assert_true('id' in content, 'Query failed: %s' % (content,))

      query_id = content['id']
      history = beeswax.models.QueryHistory.objects.get(pk=query_id)
      assert_equal(history.query, expected_query)
      assert_true(history.is_redacted)

      # Make sure unredacted queries are not redacted.
      query = 'SELECT "hello"'
      expected_query = 'SELECT "hello"'

      resp = make_query(c, query, database=self.db_name)
      content = json.loads(resp.content)
      query_id = content['id']
      history = beeswax.models.QueryHistory.objects.get(pk=query_id)
      assert_equal(history.query, expected_query)
      assert_false(history.is_redacted)
    finally:
      redaction.global_redaction_engine.policies = old_policies


  def test_analyze_table_and_read_statistics(self):
    _make_query(self.client, "USE %s" % self.db_name, wait=True) # We need this until Hive 1.2

    try:
      # Retrieve stats before analyze
      resp = self.client.get(reverse('beeswax:get_table_stats', kwargs={'database': self.db_name, 'table': 'test'}))
      stats = json.loads(resp.content)['stats']
      assert_true(any([stat for stat in stats if stat['data_type'] == 'numRows' and stat['comment'] == '0']), resp.content)

      resp = self.client.get(reverse('beeswax:get_table_stats', kwargs={'database': self.db_name, 'table': 'test', 'column': 'foo'}))
      stats = json.loads(resp.content)['stats']
      assert_equal([
            {u'col_name': u'foo'},
            {u'data_type': u'int'},
            {u'min': u''},
            {u'max': u''},
            {u'num_nulls': u''},
            {u'distinct_count': u''},
            {u'avg_col_len': u''},
            {u'max_col_len': u''},
            {u'num_trues': u''},
            {u'num_falses': u''}
          ],
          stats
      )

      # Compute stats
      response = self.client.post(reverse("beeswax:analyze_table", kwargs={'database': self.db_name, 'table': 'test'}), follow=True)
      response = wait_for_query_to_finish(self.client, response, max=120.0)
      assert_true(response, response)

      response = self.client.post(reverse("beeswax:analyze_table", kwargs={'database': self.db_name, 'table': 'test', 'columns': True}), follow=True)
      response = wait_for_query_to_finish(self.client, response, max=120.0)
      assert_true(response, response)

      # Retrieve stats after analyze
      resp = self.client.get(reverse('beeswax:get_table_stats', kwargs={'database': self.db_name, 'table': 'test'}))
      stats = json.loads(resp.content)['stats']
      assert_true(any([stat for stat in stats if stat['data_type'] == 'numRows' and stat['comment'] == '256']), resp.content)

      resp = self.client.get(reverse('beeswax:get_table_stats', kwargs={'database': self.db_name, 'table': 'test', 'column': 'foo'}))
      stats = json.loads(resp.content)['stats']
      assert_equal([
          {u'col_name': u'foo'},
          {u'data_type': u'int'},
          {u'min': u'0'},
          {u'max': u'255'},
          {u'num_nulls': u'0'},
          {u'distinct_count': u'180'},
          {u'avg_col_len': u''},
          {u'max_col_len': u''},
          {u'num_trues': u''},
          {u'num_falses': u''}
        ],
        stats
      )
    finally:
      _make_query(self.client, "USE default", wait=True)


  def test_get_top_terms(self):
    if is_live_cluster():
      raise SkipTest('HUE-2902: Skipping because test is not reentrant')
    else:
      raise SkipTest('HUE-2902: Skipping because test is slow currently and API is not used')

    resp = self.client.get(reverse("beeswax:get_top_terms", kwargs={'database': self.db_name, 'table': 'test', 'column': 'foo'}))

    content = json.loads(resp.content)
    assert_true('terms' in content, 'Failed to get terms: %s' % (content,))
    terms = content['terms']

    assert_equal([[255, 1], [254, 1], [253, 1], [252, 1]], terms[:4])

    resp = self.client.get(reverse("beeswax:get_top_terms", kwargs={'database': self.db_name, 'table': 'test', 'column': 'foo', 'prefix': '10'}))

    content = json.loads(resp.content)
    assert_true('terms' in content, 'Failed to get terms: %s' % (content,))
    terms = content['terms']

    assert_equal([[109, 1], [108, 1], [107, 1], [106, 1]], terms[:4])

    resp = self.client.get(reverse("beeswax:get_top_terms", kwargs={'database': self.db_name, 'table': 'test', 'column': 'foo', 'prefix': '10'}) + '?limit=2')

    content = json.loads(resp.content)
    assert_true('terms' in content, 'Failed to get terms: %s' % (content,))
    terms = content['terms']

    assert_equal([[109, 1], [108, 1]], terms)


  def test_beeswax_api_autocomplete(self):
    CREATE_TABLE = "CREATE TABLE `%(db)s`.`nested_table` (foo ARRAY<STRUCT<bar:INT, baz:STRING>>);" % {'db': self.db_name}
    _make_query(self.client, CREATE_TABLE, wait=True)

    resp = self.client.get(reverse("beeswax:api_autocomplete_databases", kwargs={}))
    databases = json.loads(resp.content)['databases']
    assert_true(self.db_name in databases)

    # Autocomplete tables for a given database
    resp = self.client.get(reverse("beeswax:api_autocomplete_tables", kwargs={'database': self.db_name}))
    tables = json.loads(resp.content)['tables_meta']
    assert_true("nested_table" in [table['name'] for table in tables])

    # Autocomplete columns for a given table
    resp = self.client.get(reverse("beeswax:api_autocomplete_columns", kwargs={'database': self.db_name, 'table': 'nested_table'}))
    columns = json.loads(resp.content)['columns']
    assert_true("foo" in columns)
    extended_columns = json.loads(resp.content)['extended_columns']
    assert_equal({'comment': '', 'type': 'array<struct<bar:int,baz:string>>', 'name': 'foo'}, extended_columns[0])

    # Autocomplete nested fields for a given column
    resp = self.client.get(reverse("beeswax:api_autocomplete_column", kwargs={'database': self.db_name, 'table': 'nested_table', 'column': 'foo'}))
    json_resp = json.loads(resp.content)
    assert_false('error' in json_resp, 'Failed to autocomplete nested type: %s' % json_resp.get('error'))

    assert_equal("array", json_resp['type'])
    assert_true("item" in json_resp)
    assert_equal("struct", json_resp["item"]["type"])

    # Autocomplete nested fields for a given nested type
    resp = self.client.get(reverse("beeswax:api_autocomplete_nested", kwargs={'database': self.db_name, 'table': 'nested_table', 'column': 'foo', 'nested': 'item'}))
    json_resp = json.loads(resp.content)
    assert_false('error' in json_resp, 'Failed to autocomplete nested type: %s' % json_resp.get('error'))

    assert_equal("struct", json_resp['type'])
    assert_true("fields" in json_resp)


  def test_get_indexes(self):
    table_name = 'indexed_table'

    hql = """
      CREATE TABLE `%(db)s`.`%(table)s` (id INT, name STRING, age INT, state STRING);
      CREATE INDEX `id_idx` ON TABLE `%(db)s`.`%(table)s` (`id`) AS 'COMPACT' WITH DEFERRED REBUILD;
      CREATE INDEX `state_idx` ON TABLE `%(db)s`.`%(table)s` (`state`) AS 'COMPACT' WITH DEFERRED REBUILD;
    """ % {'db': self.db_name, 'table': table_name}
    _make_query(self.client, hql, wait=True, local=False, max=180.0, database=self.db_name)

    resp = self.client.get(reverse("beeswax:get_indexes", kwargs={'database': self.db_name, 'table': table_name}))
    json_resp = json.loads(resp.content)
    assert_true('headers' in json_resp, json_resp)
    assert_true('rows' in json_resp, json_resp)
    assert_equal(2, len(json_resp['rows']), json_resp['rows'])


  def test_get_settings(self):
    resets = [
      beeswax.conf.CONFIG_WHITELIST.set_for_testing('hive.execution.engine,mapreduce.job.queuename'),
    ]

    try:
      resp = self.client.get(reverse("beeswax:get_settings"))
      json_resp = json.loads(resp.content)
      assert_equal(0, json_resp['status'])
      assert_equal(2, len(list(json_resp['settings'].items())), json_resp)
      assert_true('hive.execution.engine' in json_resp['settings'])
      assert_true('mapreduce.job.queuename' in json_resp['settings'])
    finally:
      for reset in resets:
        reset()


  def test_get_functions(self):
    resp = self.client.get(reverse("beeswax:get_functions"))
    json_resp = json.loads(resp.content)
    assert_true('functions' in json_resp, json_resp)
    assert_true('coalesce' in json_resp['functions'], json_resp['functions'])

    resp = self.client.get(reverse("beeswax:get_functions"), {'prefix': 'a'})
    json_resp = json.loads(resp.content)
    assert_true('functions' in json_resp, json_resp)
    assert_true('avg' in json_resp['functions'], json_resp['functions'])
    assert_false('coalesce' in json_resp['functions'], json_resp['functions'])


  def test_databases_quote(self):
    c = self.client
    db_name = '__%s' % self.db_name
    _make_query(c, "CREATE DATABASE IF NOT EXISTS `%s`" % db_name, database=self.db_name)

    try:
      self.db.use(db_name)
      self.db.get_tables(db_name)
    finally:
      self.db.use(self.db_name)
      _make_query(c, "DROP DATABASE IF EXISTS `%s`" % db_name, database=self.db_name)


  def test_hs2_log_verbose(self):
    """
    Test that the HS2 logs send back the ql.Driver log output with JobID
    """
    execution_engines = get_available_execution_engines()

    for engine in execution_engines:
      hql = "SELECT foo FROM `%(db)s`.`test` GROUP BY foo" % {'db': self.db_name}  # GROUP BY forces the MR job
      response = _make_query(self.client, hql, wait=True, local=False, max=180.0, database=self.db_name,
                             settings=[('hive.execution.engine', engine)])
      content = fetch_query_result_data(self.client, response)

      log = content['log']
      assert_true(search_log_line('Completed executing command', log), log)
      # Test job extraction while we're at it
      assert_equal(1, len(parse_out_jobs(log, engine)), "Should have started 1 job and extracted it.")



def test_import_gzip_reader():
  """Test the gzip reader in create table"""
  # Make gzipped data
  data = file(__file__).read()
  data_gz_sio = string_io()
  gz = gzip.GzipFile(fileobj=data_gz_sio, mode='wb')
  gz.write(data)
  gz.close()
  data_gz = data_gz_sio.getvalue()

  # Make sure we can't look at the whole gzipped data
  old_peek_size = beeswax.create_table.IMPORT_PEEK_SIZE
  beeswax.create_table.IMPORT_PEEK_SIZE = len(data_gz) - 1024
  try:
    reader = beeswax.create_table.GzipFileReader
    lines = reader.readlines(data_gz_sio, 'utf-8')
    assert_true(lines is not None)
    lines_joined = '\n'.join(lines)
    assert_equal(data[:len(lines_joined)], lines_joined)
  finally:
    beeswax.create_table.IMPORT_PEEK_SIZE = old_peek_size


def test_index_page():
  """Minimal test that index page renders."""
  c = make_logged_in_client()
  c.get("/beeswax")


def test_history_page():
  raise SkipTest

  client = make_logged_in_client()
  test_user = User.objects.get(username='test')

  query, created = SavedQuery.objects.get_or_create(
    type=HQL,
    owner=test_user,
    data='HQL query...',
    name='Test query',
    desc='Description',
  )

  QueryHistory.objects.get_or_create(
      owner=test_user,
      query='SELECT',
      design=query,
      last_state=0,
      has_results=True,
      query_type=HQL
  )


  def do_view(param, n=1):
    resp = client.get('/beeswax/query_history?' + param)
    if n == 0:
      if resp.context[0]['page']:
        assert_equal(len(resp.context[0]['page'].object_list), 0)
    else:
      assert_true(len(resp.context[0]['page'].object_list) >= n)     # Make the query run
    return resp

  do_view('')
  do_view('q-user=test')
  do_view('q-user=test_who', 0)
  do_view('q-user=:all')
  do_view('q-design_id=%s' % query.id)
  do_view('q-design_id=9999999', 0)
  do_view('q-auto_query=0')
  do_view('q-auto_query=1')
  do_view('sort=date')
  do_view('sort=-date')
  do_view('sort=state')
  do_view('sort=-state')
  do_view('sort=name')
  do_view('sort=-name')
  do_view('sort=type')
  do_view('sort=-type')
  do_view('sort=name&user=bogus&design_id=1&auto_query=1')
  do_view('sort=-type&user=:all&type=hql&auto_query=0')

  # Only show Beeswax queries
  response = do_view('')
  assert_equal({u'q-type': [u'beeswax']}, response.context[0]['filter_params'])

  # Test pagination
  response = do_view('q-page=100', 0)
  if response.context[0]['page']:
    assert_equal(0, len(response.context[0]['page'].object_list))

  client = make_logged_in_client(username='test_who')
  grant_access('test_who', 'test_who', 'test_who')
  do_view('q-user=test_who', 0)
  do_view('q-user=:all')


def test_hadoop_extraction():
  sample_log = """
Starting Job = job_201003191517_0002, Tracking URL = http://localhost:50030/jobdetails.jsp?jobid=job_201003191517_0002
    --- we should be ignoring duplicates ---
Starting Job = job_201003191517_0002, Tracking URL = http://localhost:50030/jobdetails.jsp?jobid=job_201003191517_0002
Starting Job = job_201003191517_0003, Tracking URL = http://localhost:50030/jobdetails.jsp?jobid=job_201003191517_0003
14/06/10 14:30:55 INFO exec.Task: Starting Job = job_1402420825148_0001, Tracking URL = http://localhost:8088/proxy/application_1402420825148_0001/
"""
  assert_equal(
    ["job_201003191517_0002", "job_201003191517_0003", "job_1402420825148_0001"],
    parse_out_jobs(sample_log))
  assert_equal([], parse_out_jobs("nothing to see here"))

  sample_log_no_direct_url = """
14/06/09 08:40:38 INFO impl.YarnClientImpl: Submitted application application_1402269517321_0003
14/06/09 08:40:38 INFO mapreduce.Job: The url to track the job: N/A
14/06/09 08:40:38 INFO exec.Task: Starting Job = job_1402269517321_0003, Tracking URL = N/A
14/06/09 08:40:38 INFO exec.Task: Kill Command = /usr/lib/hadoop/bin/hadoop job  -kill job_1402269517321_0003
14/06/09 08:40:38 INFO cli.CLIService: OperationHandle [opType=EXECUTE_STATEMENT, getHandleIdentifier()=2168d15e-96d2-415a-8d49-e2535e82c2a4]: getOperationStatus()
"""
  assert_equal(
      ["job_1402269517321_0003"],
      parse_out_jobs(sample_log_no_direct_url))


def test_tez_job_extraction():
  sample_log = """
16/07/12 05:47:08 INFO SessionState:
16/07/12 05:47:08 INFO SessionState: Status: Running (Executing on YARN cluster with App id application_1465862139975_0002)
16/07/12 05:47:08 INFO SessionState: Map 1: -/-	Reducer 2: 0/1
"""

  assert_equal(["application_1465862139975_0002"], parse_out_jobs(sample_log, 'tez'))
  assert_equal([], parse_out_jobs("Tez job doesn't exist.", 'tez'))


def test_hive_site():
  tmpdir = tempfile.mkdtemp()
  saved = None
  try:
    # We just replace the Beeswax conf variable
    class Getter(object):
      def get(self):
        return tmpdir

    xml = hive_site_xml(is_local=True, use_sasl=False)
    file(os.path.join(tmpdir, 'hive-site.xml'), 'w').write(xml)

    beeswax.hive_site.reset()
    saved = beeswax.conf.HIVE_CONF_DIR
    beeswax.conf.HIVE_CONF_DIR = Getter()

    assert_equal(beeswax.hive_site.get_conf()['hive.metastore.warehouse.dir'], u'/abc')
    assert_equal(beeswax.hive_site.get_hiveserver2_kerberos_principal('localhost'), 'hs2test/test.com@TEST.COM')
    assert_equal(beeswax.hive_site.get_hiveserver2_authentication(), 'NOSASL')
  finally:
    beeswax.hive_site.reset()
    if saved is not None:
      beeswax.conf.HIVE_CONF_DIR = saved
    shutil.rmtree(tmpdir)


def test_hive_site_host_pattern_local_host():
  hostname = socket.getfqdn()
  tmpdir = tempfile.mkdtemp()
  saved = None
  try:
    # We just replace the Beeswax conf variable
    class Getter(object):
      def get(self):
        return tmpdir

    thrift_uris = 'thrift://%s:9999' % hostname
    xml = hive_site_xml(is_local=False, use_sasl=False, thrift_uris=thrift_uris, kerberos_principal='test/_HOST@TEST.COM', hs2_kerberos_principal='test/_HOST@TEST.COM')
    file(os.path.join(tmpdir, 'hive-site.xml'), 'w').write(xml)

    beeswax.hive_site.reset()
    saved = beeswax.conf.HIVE_CONF_DIR
    beeswax.conf.HIVE_CONF_DIR = Getter()

    reset = []
    reset.append(beeswax.conf.HIVE_SERVER_HOST.set_for_testing(hostname))

    assert_equal(beeswax.hive_site.get_conf()['hive.metastore.warehouse.dir'], u'/abc')
    assert_equal(beeswax.hive_site.get_hiveserver2_kerberos_principal(hostname), 'test/' + socket.getfqdn().lower() + '@TEST.COM')
  finally:
    for finish in reset:
      finish()
    beeswax.hive_site.reset()
    if saved is not None:
      beeswax.conf.HIVE_CONF_DIR = saved
    shutil.rmtree(tmpdir)


def test_hive_site_null_hs2krb():
  """Test hive-site parsing with null hs2 kerberos principal"""
  tmpdir = tempfile.mkdtemp()
  saved = None
  try:
    # We just replace the Beeswax conf variable
    class Getter(object):
      def get(self):
        return tmpdir

    xml = hive_site_xml(is_local=True, use_sasl=False, hs2_kerberos_principal=None)
    file(os.path.join(tmpdir, 'hive-site.xml'), 'w').write(xml)

    beeswax.hive_site.reset()
    saved = beeswax.conf.HIVE_CONF_DIR
    beeswax.conf.HIVE_CONF_DIR = Getter()

    assert_equal(beeswax.hive_site.get_conf()['hive.metastore.warehouse.dir'], u'/abc')
    assert_equal(beeswax.hive_site.get_hiveserver2_kerberos_principal('localhost'), None)
    assert_equal(beeswax.hive_site.get_hiveserver2_authentication(), 'NOSASL')
  finally:
    beeswax.hive_site.reset()
    if saved is not None:
      beeswax.conf.HIVE_CONF_DIR = saved
    shutil.rmtree(tmpdir)


def test_collapse_whitespace():
  assert_equal("", collapse_whitespace("\t\n\n  \n\t \n"))
  assert_equal("x", collapse_whitespace("\t\nx\n  \n\t \n"))
  assert_equal("x y", collapse_whitespace("\t\nx\n  \ny\t \n"))


def test_search_log_line():
  logs = """
    FAILED: Parse Error: line 1:31 cannot recognize input near '''' '_this_is_not' 'SQL' in constant
    2012-08-18 12:23:15,648 ERROR [pool-1-thread-2] ql.Driver (SessionState.java:printError(380)) - FAILED: Parse Error: line 1:31 cannot recognize input near '''' '_this_is_not' 'SQL' in constant
    org.apache.hadoop.hive.ql.parse.ParseException: line 1:31 cannot recognize input near '''' '_this_is_not' 'SQL' in constant
    """
  assert_true(search_log_line('FAILED: Parse Error', logs))

  logs = "12/08/22 20:50:14 ERROR ql.Driver: FAILED: Parse Error: line 1:31 cannot recognize input near '''' '_this_is_not' 'SQL' in constant'"
  assert_true(search_log_line('FAILED: Parse Error', logs))

  logs = """
    FAILED: Parse Error: line 1:31 cannot recognize input near '''' '_this_is_not' 'SQL' in constant
    2012-08-18 12:23:15,648 ERROR [pool-1-thread-2] ql.Driver (SessionState.java:printError(380)) - FAILED: Parse XXXX Error: line 1:31 cannot recognize input near '''' '_this_is_not' 'SQL' in constant
    org.apache.hadoop.hive.ql.parse.ParseException: line 1:31 cannot recognize input near '''' '_this_is_not' 'SQL' in constant
    """
  assert_false(search_log_line('FAILED: Undefined', logs))

  logs = """
    2012-08-18 12:23:15,648 ERROR [pool-1-thread-2] ql.Driver (SessionState.java:printError(380)) - FAILED: Parse
    Error: line 1:31 cannot recognize input near '''' '_this_is_not' 'SQL' in constant
    """
  assert_false(search_log_line('FAILED: Parse Error', logs))


  query_with_comments = """--First query;
select concat('--', name)  -- The '--' in quotes is not a comment
where id = '10';
-- Second query
select * where id = '10';"""
  assert_equal(["--First query;\nselect concat(\'--\', name)  -- The \'--\' in quotes is not a comment\nwhere id = \'10\'",
"-- Second query\nselect * where id = \'10\'"], hql_query(query_with_comments).statements)

  query = """CREATE DATABASE IF NOT EXISTS functional;
DROP TABLE IF EXISTS functional.alltypes;
CREATE EXTERNAL TABLE IF NOT EXISTS functional.alltypes (
id int COMMENT 'Add a comment',
bool_col boolean,
tinyint_col tinyint,
smallint_col smallint,
int_col int,
bigint_col bigint,
float_col float,
double_col double,
date_string_col string,
string_col string,
timestamp_col timestamp)
PARTITIONED BY (year int, month int)
ROW FORMAT delimited fields terminated by ','  escaped by '\\\\'
STORED AS TEXTFILE
LOCATION '/user/admin/alltypes/alltypes';

USE functional;
ALTER TABLE alltypes ADD IF NOT EXISTS PARTITION(year=2009, month=1);
ALTER TABLE alltypes ADD IF NOT EXISTS PARTITION(year=2009, month=2);"""
  assert_equal(['CREATE DATABASE IF NOT EXISTS functional',
                'DROP TABLE IF EXISTS functional.alltypes',
                "CREATE EXTERNAL TABLE IF NOT EXISTS functional.alltypes (\nid int COMMENT 'Add a comment',\nbool_col boolean,\ntinyint_col tinyint,\nsmallint_col smallint,\nint_col int,\nbigint_col bigint,\nfloat_col float,\ndouble_col double,\ndate_string_col string,\nstring_col string,\ntimestamp_col timestamp)\nPARTITIONED BY (year int, month int)\nROW FORMAT delimited fields terminated by ','  escaped by '\\\\'\nSTORED AS TEXTFILE\nLOCATION '/user/admin/alltypes/alltypes'",
                'USE functional',
                'ALTER TABLE alltypes ADD IF NOT EXISTS PARTITION(year=2009, month=1)',
                'ALTER TABLE alltypes ADD IF NOT EXISTS PARTITION(year=2009, month=2)'
              ],
              hql_query(query).statements, hql_query(query).statements)


class MockHiveServerTable(HiveServerTable):

  def __init__(self, describe=None):
    if describe is not None:
      self.describe = describe
    else:
      self.describe = [
            {'comment': 'comment             ', 'col_name': '# col_name            ', 'data_type': 'data_type           '},
            {'comment': None, 'col_name': '', 'data_type': None},
            {'comment': '', 'col_name': 'foo', 'data_type': 'int'},
            {'comment': '', 'col_name': 'bar', 'data_type': 'string'},
            {'comment': None, 'col_name': '', 'data_type': None},
            {'comment': None, 'col_name': '# Partition Information', 'data_type': None},
            {'comment': 'comment             ', 'col_name': '# col_name            ', 'data_type': 'data_type           '},
            {'comment': None, 'col_name': '', 'data_type': None},
            {'comment': '', 'col_name': 'baz', 'data_type': 'string'},
            {'comment': '', 'col_name': 'boom', 'data_type': 'string'},
            {'comment': None, 'col_name': '', 'data_type': None},
            {'comment': None, 'col_name': '# Detailed Table Information', 'data_type': None},
            {'comment': None, 'col_name': 'Database:           ', 'data_type': 'default             '},
            {'comment': None, 'col_name': 'Owner:              ', 'data_type': 'romain              '},
            {'comment': None, 'col_name': 'CreateTime:         ', 'data_type': 'Wed Aug 13 13:39:53 PDT 2014'},
            {'comment': None, 'col_name': 'LastAccessTime:     ', 'data_type': 'UNKNOWN             '},
            {'comment': None, 'col_name': 'Protect Mode:       ', 'data_type': 'None                '},
            {'comment': None, 'col_name': 'Retention:          ', 'data_type': '0                   '},
            {'comment': None, 'col_name': 'Location:           ', 'data_type': 'hdfs://localhost:8020/user/hive/warehouse/test_partitions'},
            {'comment': None, 'col_name': 'Table Type:         ', 'data_type': 'MANAGED_TABLE       '},
            {'comment': None, 'col_name': 'Table Parameters:', 'data_type': None},
            {'comment': '1407962393          ', 'col_name': '', 'data_type': 'transient_lastDdlTime'},
            {'comment': None, 'col_name': '', 'data_type': None},
            {'comment': None, 'col_name': '# Storage Information', 'data_type': None},
            {'comment': None, 'col_name': 'SerDe Library:      ', 'data_type': 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'},
            {'comment': None, 'col_name': 'InputFormat:        ', 'data_type': 'org.apache.hadoop.mapred.TextInputFormat'},
            {'comment': None, 'col_name': 'OutputFormat:       ', 'data_type': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'},
            {'comment': None, 'col_name': 'Compressed:         ', 'data_type': 'No                  '},
            {'comment': None, 'col_name': 'Num Buckets:        ', 'data_type': '-1                  '},
            {'comment': None, 'col_name': 'Bucket Columns:     ', 'data_type': '[]                  '},
            {'comment': None, 'col_name': 'Sort Columns:       ', 'data_type': '[]                  '},
            {'comment': None, 'col_name': 'Storage Desc Params:', 'data_type': None},
            {'comment': '\\t                  ', 'col_name': '', 'data_type': 'field.delim         '},
            {'comment': '\\n                  ', 'col_name': '', 'data_type': 'line.delim          '},
            {'comment': '\\t                  ', 'col_name': '', 'data_type': 'serialization.format'}
        ]
    self.is_impala_only = False


class MockHiveServerTableForPartitions(HiveServerTable):

  def __init__(self, describe=None):
    if describe is not None:
      self.describe = describe
    else:
      self.describe = [
        {'comment': 'comment             ', 'col_name': '# col_name            ', 'data_type': 'data_type           '},
        {'comment': 'NULL', 'col_name': '', 'data_type': 'NULL'},
        {'comment': 'from deserializer', 'col_name': 'f1', 'data_type': 'string'},
        {'comment': 'from deserializer', 'col_name': 'f2', 'data_type': 'string'},
        {'comment': 'from deserializer', 'col_name': 'f3', 'data_type': 'string'},
        {'comment': 'from deserializer', 'col_name': 'f4', 'data_type': 'string'},
        {'comment': 'from deserializer', 'col_name': 'f5', 'data_type': 'string'},
        {'comment': 'from deserializer', 'col_name': 'f6', 'data_type': 'string'},
        {'comment': 'from deserializer', 'col_name': 'f7', 'data_type': 'string'},
        {'comment': 'from deserializer', 'col_name': 'f8', 'data_type': 'string'},
        {'comment': 'from deserializer', 'col_name': 'f9', 'data_type': 'string'},
        {'comment': 'from deserializer', 'col_name': 'f10', 'data_type': 'string'},
        {'comment': 'from deserializer', 'col_name': 'f11', 'data_type': 'string'},
        {'comment': 'from deserializer', 'col_name': 'f12', 'data_type': 'string'},
        {'comment': 'from deserializer', 'col_name': 'f13', 'data_type': 'bigint'},
        {'comment': 'from deserializer', 'col_name': 'f14', 'data_type': 'int'},
        {'comment': 'from deserializer', 'col_name': 'f15', 'data_type': 'string'},
        {'comment': 'from deserializer', 'col_name': 'f16', 'data_type': 'string'},
        {'comment': 'from deserializer', 'col_name': 'f17', 'data_type': 'string'},
        {'comment': 'from deserializer', 'col_name': 'f18', 'data_type': 'timestamp'},
        {'comment': 'from deserializer', 'col_name': 'f19', 'data_type': 'int'},
        {'comment': 'from deserializer', 'col_name': 'f20', 'data_type': 'int'},
        {'comment': 'from deserializer', 'col_name': 'f21', 'data_type': 'string'},
        {'comment': 'from deserializer', 'col_name': 'f22', 'data_type': 'string'},
        {'comment': 'from deserializer', 'col_name': 'f23', 'data_type': 'string'},
        {'comment': 'from deserializer', 'col_name': 'f24', 'data_type': 'string'},
        {'comment': 'from deserializer', 'col_name': 'f25', 'data_type': 'timestamp'},
        {'comment': 'from deserializer', 'col_name': 'f26', 'data_type': 'int'},
        {'comment': 'from deserializer', 'col_name': 'f27', 'data_type': 'binary'},
        {'comment': 'NULL', 'col_name': '', 'data_type': 'NULL'},
        {'comment': 'NULL', 'col_name': '# Partition Information', 'data_type': 'NULL'},
        {'comment': 'comment             ', 'col_name': '# col_name            ', 'data_type': 'data_type           '},
        {'comment': 'NULL', 'col_name': '', 'data_type': 'NULL'},
        {'comment': '', 'col_name': 'import_date', 'data_type': 'string'},
        {'comment': '', 'col_name': 'import_id', 'data_type': 'int'},
        {'comment': 'NULL', 'col_name': '', 'data_type': 'NULL'},
        {'comment': 'NULL', 'col_name': '# Detailed Table Information', 'data_type': 'NULL'},
        {'comment': 'NULL', 'col_name': 'Database:           ', 'data_type': 'my_db           '},
        {'comment': 'NULL', 'col_name': 'Owner:              ', 'data_type': 'hive                '},
        {'comment': 'NULL', 'col_name': 'CreateTime:         ', 'data_type': 'Wed Feb 10 14:29:49 UTC 2016'},
        {'comment': 'NULL', 'col_name': 'LastAccessTime:     ', 'data_type': 'UNKNOWN             '},
        {'comment': 'NULL', 'col_name': 'Protect Mode:       ', 'data_type': 'None                '},
        {'comment': 'NULL', 'col_name': 'Retention:          ', 'data_type': '0                   '},
        {'comment': 'NULL', 'col_name': 'Location:           ', 'data_type': 'hdfs://nameservice1/folder/folder'},
        {'comment': 'NULL', 'col_name': 'Table Type:         ', 'data_type': 'EXTERNAL_TABLE      '},
        {'comment': 'NULL', 'col_name': 'Table Parameters:', 'data_type': 'NULL'},
        {'comment': 'TRUE                ', 'col_name': '', 'data_type': 'EXTERNAL            '},
        {'comment': '1455114589          ', 'col_name': '', 'data_type': 'transient_lastDdlTime'},
        {'comment': 'NULL', 'col_name': '', 'data_type': 'NULL'},
        {'comment': 'NULL', 'col_name': '# Storage Information', 'data_type': 'NULL'},
        {'comment': 'NULL', 'col_name': 'SerDe Library:      ', 'data_type': 'com.x.y.z.a.MyDeserializer'},
        {'comment': 'NULL', 'col_name': 'InputFormat:        ', 'data_type': 'com.x.y.z.a.MyInputFormat'},
        {'comment': 'NULL', 'col_name': 'OutputFormat:       ', 'data_type': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'},
        {'comment': 'NULL', 'col_name': 'Compressed:         ', 'data_type': 'No                  '},
        {'comment': 'NULL', 'col_name': 'Num Buckets:        ', 'data_type': '-1                  '},
        {'comment': 'NULL', 'col_name': 'Bucket Columns:     ', 'data_type': '[]                  '},
        {'comment': 'NULL', 'col_name': 'Sort Columns:       ', 'data_type': '[]                  '},
        {'comment': 'NULL', 'col_name': 'Storage Desc Params:', 'data_type': 'NULL'},
        {'comment': '1       ', 'col_name': '', 'data_type': 'serialization.format'},
      ]
    self.is_impala_only = False



class TestHiveServer2API(object):

  def test_parsing_partition_values(self):
    table = MockHiveServerTable()

    value = PartitionValueCompatible(['datehour=2013022516'], table)
    assert_equal(['2013022516'], value.values)

    value = PartitionValueCompatible(['month=2011-07/dt=2011-07-01/hr=12'], table)
    assert_equal(['2011-07', '2011-07-01', '12'], value.values)


  def test_hiveserver_table(self):
    table = MockHiveServerTable()

    assert_equal([
        {'comment': None, 'col_name': '# Partition Information', 'data_type': None},
        {'comment': 'comment', 'col_name': '# col_name', 'data_type': 'data_type'},
        {'comment': None, 'col_name': '', 'data_type': None},
        {'comment': '', 'col_name': 'baz', 'data_type': 'string'},
        {'comment': '', 'col_name': 'boom', 'data_type': 'string'},
        {'comment': None, 'col_name': '', 'data_type': None},
        {'comment': None, 'col_name': '# Detailed Table Information', 'data_type': None},
        {'comment': None, 'col_name': 'Database:', 'data_type': 'default'},
        {'comment': None, 'col_name': 'Owner:', 'data_type': 'romain'},
        {'comment': None, 'col_name': 'CreateTime:', 'data_type': 'Wed Aug 13 13:39:53 PDT 2014'},
        {'comment': None, 'col_name': 'LastAccessTime:', 'data_type': 'UNKNOWN'},
        {'comment': None, 'col_name': 'Protect Mode:', 'data_type': 'None'},
        {'comment': None, 'col_name': 'Retention:', 'data_type': '0'},
        {'comment': None, 'col_name': 'Location:', 'data_type': 'hdfs://localhost:8020/user/hive/warehouse/test_partitions'},
        {'comment': None, 'col_name': 'Table Type:', 'data_type': 'MANAGED_TABLE'},
        {'comment': None, 'col_name': 'Table Parameters:', 'data_type': None},
        {'comment': '1407962393', 'col_name': '', 'data_type': 'transient_lastDdlTime'},
        {'comment': None, 'col_name': '', 'data_type': None},
        {'comment': None, 'col_name': '# Storage Information', 'data_type': None},
        {'comment': None, 'col_name': 'SerDe Library:', 'data_type': 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'},
        {'comment': None, 'col_name': 'InputFormat:', 'data_type': 'org.apache.hadoop.mapred.TextInputFormat'},
        {'comment': None, 'col_name': 'OutputFormat:', 'data_type': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'},
        {'comment': None, 'col_name': 'Compressed:', 'data_type': 'No'},
        {'comment': None, 'col_name': 'Num Buckets:', 'data_type': '-1'},
        {'comment': None, 'col_name': 'Bucket Columns:', 'data_type': '[]'},
        {'comment': None, 'col_name': 'Sort Columns:', 'data_type': '[]'},
        {'comment': None, 'col_name': 'Storage Desc Params:', 'data_type': None},
        {'comment': '\\t', 'col_name': '', 'data_type': 'field.delim'},
        {'comment': '\\n', 'col_name': '', 'data_type': 'line.delim'},
        {'comment': '\\t', 'col_name': '', 'data_type': 'serialization.format'}
        ],
        table.properties
    )

    assert_equal('hdfs://localhost:8020/user/hive/warehouse/test_partitions', table.path_location)

    assert_equal([
      {'col_name': 'foo', 'comment': '', 'data_type': 'int'},
      {'col_name': 'bar', 'comment': '', 'data_type': 'string'},
      {'col_name': 'baz', 'comment': '', 'data_type': 'string'},
      {'col_name': 'boom', 'comment': '', 'data_type': 'string'}], table.cols)

    assert_equal([PartitionKeyCompatible('baz', 'string', ''),
                  PartitionKeyCompatible('boom', 'string', '')
                 ], table.partition_keys)


  def test_hiveserver_table_for_partitions(self):
    table = MockHiveServerTableForPartitions()

    assert_equal([
        PartitionKeyCompatible('import_date', 'string', ''),
        PartitionKeyCompatible('import_id', 'int', '')
      ], table.partition_keys
    )


  def test_hiveserver_has_complex(self):
    # Test simple table with only scalars
    table = MockHiveServerTable()
    assert_false(table.has_complex, table.cols)

    # Test complex table with array column
    table.describe.insert(4, {'comment': '', 'col_name': 'fizz', 'data_type': 'array<string>'})
    assert_true(table.has_complex, table.cols)


  def test_hiveserver_table_partition_keys(self):
    describe = [
        {'comment': None, 'col_name': '# Partition Information', 'data_type': None},
        {'comment': 'comment             ', 'col_name': '# col_name            ', 'data_type': 'data_type           '},
        {'comment': None, 'col_name': '', 'data_type': None},
        {'comment': '', 'col_name': 'dt', 'data_type': 'string'},
        {'comment': '', 'col_name': 'country', 'data_type': 'string'},
        {'comment': 'this, has extra: sigils', 'col_name': 'decimal', 'data_type': 'decimal(9, 7)'},
        {'comment': '', 'col_name': 'complex', 'data_type': 'UNIONTYPE<int, double, array<string>, struct<a:int,b:string>>'},
        {'comment': None, 'col_name': '', 'data_type': None}
    ]
    table = MockHiveServerTable(describe)

    assert_equal([PartitionKeyCompatible('dt', 'string', ''),
                  PartitionKeyCompatible('country', 'string', ''),
                  PartitionKeyCompatible('decimal', 'decimal(9, 7)', 'this, has extra: sigils'),
                  PartitionKeyCompatible('complex', 'UNIONTYPE<int, double, array<string>, struct<a:int,b:string>>', ''),
                 ], table.partition_keys)


  def test_column_format_values_nulls(self):
    data = [1, 1, 1]
    nulls = '\x00'

    assert_equal([1, 1, 1],
                 HiveServerTColumnValue2.set_nulls(data, nulls))

    data = [1, 1, 1]
    nulls = '\x03'

    assert_equal([None, None, 1],
                 HiveServerTColumnValue2.set_nulls(data, nulls))

    data = [1, 1, 1, 1, 1, 1, 1, 1]
    nulls = 't' # 0b1110100

    assert_equal([1, 1, None, 1, None, None, None, 1],
                 HiveServerTColumnValue2.set_nulls(data, nulls))


    data = [1, 1, 'not_good', 'NaN', None, 'INF', 'INF', 3]
    nulls = 't' # 0b1110100

    assert_equal([1, 1, None, 'NaN', None, None, None, 3],
                 HiveServerTColumnValue2.set_nulls(data, nulls))

    data = [1] * 18
    nulls = '\xff\xee\x03'

    assert_equal([None, None, None, None, None, None, None, None, 1, None, None, None, 1, None, None, None, None, None],
                 HiveServerTColumnValue2.set_nulls(data, nulls))

    data = [1, 1, 1, 1, 1, 1, 1, 1]
    nulls = '\x41'

    assert_equal([None, 1, 1, 1, 1, 1, None, 1],
                 HiveServerTColumnValue2.set_nulls(data, nulls))

    data = [1] * 8 * 8
    nulls = '\x01\x23\x45\x67\x89\xab\xcd\xef'

    assert_equal([None, 1, 1, 1, 1, 1, 1, 1, None, None, 1, 1, 1, None, 1, 1, None, 1, None, 1, 1, 1, None, 1, None, None, None, 1, 1, None, None, 1, None, 1, 1,
                  None, 1, 1, 1, None, None, None, 1, None, 1, None, 1, None, None, 1, None, None, 1, 1, None, None, None, None, None, None, 1, None, None, None],
                 HiveServerTColumnValue2.set_nulls(data, nulls))


  def test_column_detect_if_values_nulls(self):
    data = [1, 2, 3]

    nulls = ''
    assert_true(data is HiveServerTColumnValue2.set_nulls(data, nulls))
    nulls = '\x00'
    assert_true(data is HiveServerTColumnValue2.set_nulls(data, nulls))
    nulls = '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    assert_true(data is HiveServerTColumnValue2.set_nulls(data, nulls))

    nulls = 'aaaa'
    assert_false(data is HiveServerTColumnValue2.set_nulls(data, nulls))
    nulls = '\x00\x01\x00'
    assert_false(data is HiveServerTColumnValue2.set_nulls(data, nulls))
    nulls = '\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00'
    assert_false(data is HiveServerTColumnValue2.set_nulls(data, nulls))


class MockDbms(object):

  def __init__(self, client, server_type):
    pass

  def get_databases(self):
    return ['default', 'test']

  def get_tables(self, database):
    return ['table1', 'table2']

  def get_state(self, handle):
    return 0

class TestWithMockedServer(object):

  def setUp(self):
    # Beware: Monkey patch Beeswax/Hive server with Mock API
    if not hasattr(dbms, 'OriginalBeeswaxApi'):
      dbms.OriginalBeeswaxApi = dbms.HiveServer2Dbms
    dbms.DBMS_CACHE = {}
    dbms.HiveServer2Dbms = MockDbms

    self.client = make_logged_in_client(is_superuser=False)
    self.client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test')
    self.user = User.objects.get(username='test')
    self.user_not_me = User.objects.get(username='not_me')
    grant_access("test", "test", "beeswax")

  def tearDown(self):
    dbms.DBMS_CACHE = {}
    dbms.HiveServer2Dbms = dbms.OriginalBeeswaxApi

  def test_bulk_query_trash(self):
    response = _make_query(self.client, 'SELECT', submission_type='Save', name='My Name 1', desc='My Description')
    content = json.loads(response.content)
    query = content['design_id']
    response = _make_query(self.client, 'SELECT', submission_type='Save', name='My Name 2', desc='My Description')
    content = json.loads(response.content)
    query2 = content['design_id']
    ids = [query, query2]

    resp = self.client.get('/beeswax/list_designs')
    ids_page_1 = set([query.id for query in resp.context[0]['page'].object_list])
    assert_equal(2, sum([query_id in ids_page_1 for query_id in ids]))

    resp = self.client.post(reverse('beeswax:delete_design'), {u'skipTrash': [u'false'], u'designs_selection': ids})
    queries = SavedQuery.objects.filter(id__in=ids)
    assert_true(queries[0].doc.get().is_trashed())
    assert_true(queries[1].doc.get().is_trashed())

    resp = self.client.get('/beeswax/list_designs')
    ids_page_1 = set([query.id for query in resp.context[0]['page'].object_list])
    assert_equal(0, sum([query_id in ids_page_1 for query_id in ids]))

    resp = self.client.post(reverse('beeswax:restore_design'), {u'skipTrash': [u'false'], u'designs_selection': ids})
    query = SavedQuery.objects.filter(id__in=ids)
    assert_false(queries[0].doc.get().is_trashed())
    assert_false(queries[1].doc.get().is_trashed())

    resp = self.client.get('/beeswax/list_designs')
    ids_page_1 = set([query.id for query in resp.context[0]['page'].object_list])
    assert_equal(2, sum([query_id in ids_page_1 for query_id in ids]))

    resp = self.client.post(reverse('beeswax:delete_design'), {u'skipTrash': [u'false'], u'designs_selection': ids})
    query = SavedQuery.objects.filter(id__in=ids)
    assert_true(queries[0].doc.get().is_trashed())
    assert_true(queries[1].doc.get().is_trashed())

    resp = self.client.get('/beeswax/list_designs')
    ids_page_1 = set([query.id for query in resp.context[0]['page'].object_list])
    assert_equal(0, sum([query_id in ids_page_1 for query_id in ids]))

    resp = self.client.post(reverse('beeswax:delete_design'), {u'skipTrash': [u'true'], u'designs_selection': ids})
    assert_false(SavedQuery.objects.filter(id__in=ids).exists())

    resp = self.client.get('/beeswax/list_designs')
    ids_page_1 = set([query.id for query in resp.context[0]['page'].object_list])
    assert_equal(0, sum([query_id in ids_page_1 for query_id in ids]))

  def test_save_design(self):
    response = _make_query(self.client, 'SELECT', submission_type='Save', name='My Name 1', desc='My Description')
    content = json.loads(response.content)
    design_id = content['design_id']

    design = SavedQuery.objects.get(id=design_id)
    design_obj = hql_query('SELECT')

    # Save his own query
    saved_design = _save_design(user=self.user, design=design, type_=HQL, design_obj=design_obj, explicit_save=True, name='test_save_design', desc='test_save_design desc')
    assert_equal('test_save_design', saved_design.name)
    assert_equal('test_save_design desc', saved_design.desc)
    assert_equal('test_save_design', saved_design.doc.get().name)
    assert_equal('test_save_design desc', saved_design.doc.get().description)
    assert_false(saved_design.doc.get().is_historic())

    # Execute it as auto
    saved_design = _save_design(user=self.user, design=design, type_=HQL, design_obj=design_obj, explicit_save=False, name='test_save_design', desc='test_save_design desc')
    assert_equal('test_save_design (new)', saved_design.name)
    assert_equal('test_save_design desc', saved_design.desc)
    assert_equal('test_save_design (new)', saved_design.doc.get().name)
    assert_equal('test_save_design desc', saved_design.doc.get().description)
    assert_true(saved_design.doc.get().is_historic())

    # not_me user can't modify it
    try:
      _save_design(user=self.user_not_me, design=design, type_=HQL, design_obj=design_obj, explicit_save=True, name='test_save_design', desc='test_save_design desc')
      assert_true(False, 'not_me is not allowed')
    except PopupException:
      pass

    saved_design.doc.get().share_to_default()

    try:
      _save_design(user=self.user_not_me, design=design, type_=HQL, design_obj=design_obj, explicit_save=True, name='test_save_design', desc='test_save_design desc')
      assert_true(False, 'not_me is not allowed')
    except PopupException:
      pass

    # not_me can execute it as auto
    saved_design = _save_design(user=self.user_not_me, design=design, type_=HQL, design_obj=design_obj, explicit_save=False, name='test_save_design', desc='test_save_design desc')
    assert_equal('test_save_design (new)', saved_design.name)
    assert_equal('test_save_design desc', saved_design.desc)
    assert_equal('test_save_design (new)', saved_design.doc.get().name)
    assert_equal('test_save_design desc', saved_design.doc.get().description)
    assert_true(saved_design.doc.get().is_historic())

    # not_me can save as a new design
    design = SavedQuery(owner=self.user_not_me, type=HQL)

    saved_design = _save_design(user=self.user_not_me, design=design, type_=HQL, design_obj=design_obj, explicit_save=True, name='test_save_design', desc='test_save_design desc')
    assert_equal('test_save_design', saved_design.name)
    assert_equal('test_save_design desc', saved_design.desc)
    assert_equal('test_save_design', saved_design.doc.get().name)
    assert_equal('test_save_design desc', saved_design.doc.get().description)
    assert_false(saved_design.doc.get().is_historic())

    # Save design with len(name) = 64
    response = _make_query(self.client, 'SELECT', submission_type='Save',
                name='test_character_limit', desc='test_character_limit desc')
    content = json.loads(response.content)
    design_id = content['design_id']

    design = SavedQuery.objects.get(id=design_id)
    design_obj = hql_query('SELECT')

    # Save query
    saved_design = _save_design(user=self.user, design=design, type_=HQL, design_obj=design_obj,
                                explicit_save=True, name='This__design__name__contains___sixty__five___characters___exactly', desc='test_save_design desc')
    len_after = len(saved_design.name)
    assert_equal(len_after, 64)
    saved_design = _save_design(user=self.user, design=design, type_=HQL, design_obj=design_obj,
                                explicit_save=False, name='This__design__name__contains___sixty__five___characters___exactly', desc='test_save_design desc')
    # Above design name is already 64 characters, so saved_design name shouldn't exceed the limit
    len_after = len(saved_design.name)
    assert_equal(len_after, 64)

  def test_get_history_xss(self):
    sql = 'SELECT count(sample_07.salary) FROM sample_07;"><iFrAME>src="javascript:alert(\'Hue has an xss\');"></iFraME>'
    sql_escaped = 'SELECT count(sample_07.salary) FROM sample_07;&quot;&gt;&lt;iFrAME&gt;src=&quot;javascript:alert(&#39;Hue has an xss&#39;);&quot;&gt;&lt;/iFraME&gt;'

    response = _make_query(self.client, sql, submission_type='Save', name='My Name 1', desc='My Description')
    content = json.loads(response.content)
    design_id = content['design_id']
    design = SavedQuery.objects.get(id=design_id)

    query_history = QueryHistory.build(
        owner=self.user,
        query=sql,
        server_host='server_host',
        server_port=1,
        server_name='server_name',
        server_type=HIVE_SERVER2,
        last_state=QueryHistory.STATE.submitted.value,
        design=design,
        notify=False,
        query_type=HQL,
        statement_number=0
    )
    query_history.save()

    resp = self.client.get('/beeswax/query_history?format=json')
    assert_true(sql_escaped in resp.content, resp.content)
    assert_false(sql in resp.content, resp.content)

  def test_redact_saved_design(self):
    old_policies = redaction.global_redaction_engine.policies
    redaction.global_redaction_engine.policies = [
      RedactionPolicy([
        RedactionRule('', 'ssn=\d{3}-\d{2}-\d{4}', 'ssn=XXX-XX-XXXX'),
      ])
    ]

    logfilter.add_log_redaction_filter_to_logger(redaction.global_redaction_engine, logging.root)

    try:
      # Make sure redacted queries are redacted.
      query = 'SELECT "ssn=123-45-6789"'
      expected_query = 'SELECT "ssn=XXX-XX-XXXX"'

      response = _make_query(self.client, query, submission_type='Save', name='My Name 1', desc='My Description')
      content = json.loads(response.content)
      design_id = content['design_id']

      design = SavedQuery.get(id=design_id)
      data = json.loads(design.data)

      assert_equal(data['query']['query'], expected_query)
      assert_true(design.is_redacted)

      # Make sure unredacted queries are not redacted.
      query = 'SELECT "hello"'
      expected_query = 'SELECT "hello"'

      response = _make_query(self.client, query, submission_type='Save', name='My Name 2', desc='My Description')
      content = json.loads(response.content)
      design_id = content['design_id']

      design = SavedQuery.get(id=design_id)
      data = json.loads(design.data)

      assert_equal(data['query']['query'], expected_query)
      assert_false(design.is_redacted)
    finally:
      redaction.global_redaction_engine.policies = old_policies


  def test_search_designs(self):
    # Create 20 (DEFAULT_PAGE_SIZE) queries to fill page 1, plus a target query for page 2
    page_1 = []
    for i in range(1, 21):
      response = _make_query(self.client, 'SELECT', submission_type='Save', name='My Name %d' % i, desc='My Description')
      content = json.loads(response.content)
      query_id = content['design_id']
      page_1.append(query_id)

    response = _make_query(self.client, 'SELECT', submission_type='Save', name='Test Search Design', desc='My Test Search Design')
    content = json.loads(response.content)
    query_id = content['design_id']
    page_2 = [query_id]

    resp = self.client.get(reverse('beeswax:list_designs') + '?text=Test+Search+Design')
    ids_page = set([query.id for query in resp.context[0]['page'].object_list])
    assert_equal(0, sum([query_id in ids_page for query_id in page_1]))
    assert_equal(1, sum([query_id in ids_page for query_id in page_2]))

    # Trash all designs and test search trashed designs
    ids = page_1 + page_2
    self.client.post(reverse('beeswax:delete_design'), {u'skipTrash': [u'false'], u'designs_selection': ids})
    SavedQuery.objects.filter(id__in=ids)

    resp = self.client.get(reverse('beeswax:list_trashed_designs') + '?text=Test+Search+Design')
    ids_page = set([query.id for query in resp.context[0]['page'].object_list])
    assert_equal(0, sum([query_id in ids_page for query_id in page_1]))
    assert_equal(1, sum([query_id in ids_page for query_id in page_2]))

  def test_clear_history(self):
    sql = 'SHOW TABLES'
    response = _make_query(self.client, sql, submission_type='Save', name='My clear', desc='My Description')
    content = json.loads(response.content)
    design_id = content['design_id']
    design = SavedQuery.objects.get(id=design_id)

    query_history = QueryHistory.build(
        owner=self.user,
        query=sql,
        server_host='server_host',
        server_port=1,
        server_name='server_name',
        server_type=HIVE_SERVER2,
        last_state=QueryHistory.STATE.submitted.value,
        design=design,
        notify=False,
        query_type=HQL,
        statement_number=0
    )
    query_history.save()

    resp = self.client.get(reverse('beeswax:list_query_history') + '?q-design_id=%s&format=json' % design_id)
    json_resp = json.loads(resp.content)
    design_ids = [history['design_id'] for history in json_resp['queries']]
    assert_true(design_id in design_ids, json_resp)
    resp = self.client.get(reverse('beeswax:list_query_history') + '?q-design_id=%s&recent=true&format=json' % design_id)
    json_resp = json.loads(resp.content)
    design_ids = [history['design_id'] for history in json_resp['queries']]
    assert_true(design_id in design_ids, json_resp)

    self.client.post(reverse('beeswax:clear_history'))

    resp = self.client.get(reverse('beeswax:list_query_history') + '?q-design_id=%s&format=json' % design_id)
    json_resp = json.loads(resp.content)
    design_ids = [history['design_id'] for history in json_resp['queries']]
    assert_true(design_id in design_ids, json_resp)
    resp = self.client.get(reverse('beeswax:list_query_history') + '?q-design_id=%s&recent=true&format=json' % design_id)
    json_resp = json.loads(resp.content)
    design_ids = [history['design_id'] for history in json_resp['queries']]
    assert_false(design_id in design_ids, json_resp)


class TestDesign(object):

  def test_hql_resource(self):
    design = hql_query('SELECT')
    design._data_dict['file_resources'] = [
        {'type': 'FILE', 'path': 'my_file'},
        {'type': 'FILE', 'path': '/my_path/my_file'},
        {'type': 'FILE', 'path': 's3://host/my_s3_file'}
    ]

    statements = design.get_configuration_statements()
    assert_true(re.match('ADD FILE hdfs://([^:]+):(\d+)my_file', statements[0]), statements[0])
    assert_true(re.match('ADD FILE hdfs://([^:]+):(\d+)/my_path/my_file', statements[1]), statements[1])
    assert_equal('ADD FILE s3://host/my_s3_file', statements[2])


def search_log_line(expected_log, all_logs):
  return re.compile('%(expected_log)s' % {'expected_log': expected_log}).search(all_logs)

def test_hiveserver2_get_security():
  make_logged_in_client()
  user = User.objects.get(username='test')
  # Bad but easy mocking
  hive_site.get_conf()

  prev = hive_site._HIVE_SITE_DICT.get(hive_site._CNF_HIVESERVER2_AUTHENTICATION)
  try:
    hive_site._HIVE_SITE_DICT[hive_site._CNF_HIVESERVER2_KERBEROS_PRINCIPAL] = 'hive/hive@test.com'

    principal = get_query_server_config('beeswax')['principal']
    assert_true(principal.startswith('hive/'), principal)

    principal = get_query_server_config('impala')['principal']
    assert_true(principal.startswith('impala/'), principal)

    default_query_server = {'server_host': 'my_host', 'server_port': 12345}

    # Beeswax
    beeswax_query_server = {'server_name': 'beeswax', 'principal': 'hive', 'auth_username': 'hue', 'auth_password': None}
    beeswax_query_server.update(default_query_server)
    assert_equal((True, 'PLAIN', 'hive', True, 'hue', None), HiveServerClient(beeswax_query_server, user).get_security())

    # HiveServer2 LDAP passthrough
    beeswax_query_server.update({'auth_username': 'hueabcd', 'auth_password': 'abcd'})
    assert_equal((True, 'PLAIN', 'hive', True, 'hueabcd', 'abcd'), HiveServerClient(beeswax_query_server, user).get_security())
    beeswax_query_server.update({'auth_username': 'hue', 'auth_password': None})

    hive_site._HIVE_SITE_DICT[hive_site._CNF_HIVESERVER2_AUTHENTICATION] = 'NOSASL'
    hive_site._HIVE_SITE_DICT[hive_site._CNF_HIVESERVER2_IMPERSONATION] = 'false'
    assert_equal((False, 'NOSASL', 'hive', False, 'hue', None), HiveServerClient(beeswax_query_server, user).get_security())
    hive_site._HIVE_SITE_DICT[hive_site._CNF_HIVESERVER2_AUTHENTICATION] = 'KERBEROS'
    assert_equal((True, 'GSSAPI', 'hive', False, 'hue', None), HiveServerClient(beeswax_query_server, user).get_security())

    # Impala
    cluster_conf = hadoop.cluster.get_cluster_conf_for_job_submission()

    finish = cluster_conf.SECURITY_ENABLED.set_for_testing(False)
    try:
      impala_query_server = {'server_name': 'impala', 'principal': 'impala', 'impersonation_enabled': False, 'auth_username': 'hue', 'auth_password': None}
      impala_query_server.update(default_query_server)
      assert_equal((False, 'GSSAPI', 'impala', False, 'hue', None), HiveServerClient(impala_query_server, user).get_security())

      impala_query_server = {'server_name': 'impala', 'principal': 'impala', 'impersonation_enabled': True, 'auth_username': 'hue', 'auth_password': None}
      impala_query_server.update(default_query_server)
      assert_equal((False, 'GSSAPI', 'impala', True, 'hue', None), HiveServerClient(impala_query_server, user).get_security())
    finally:
      finish()

    finish = cluster_conf.SECURITY_ENABLED.set_for_testing(True)
    try:
      assert_equal((True, 'GSSAPI', 'impala', True, 'hue', None), HiveServerClient(impala_query_server, user).get_security())
    finally:
      finish()
  finally:
    if prev is not None:
      hive_site._HIVE_SITE_DICT[hive_site._CNF_HIVESERVER2_AUTHENTICATION] = prev
    else:
      hive_site._HIVE_SITE_DICT.pop(hive_site._CNF_HIVESERVER2_AUTHENTICATION, None)


class MockClient(object):

  def __init__(self):
    self.open_session_args = None

  def OpenSession(self, args):
    self.open_session_args = args


  #def test_hive_server2_open_session():
  #  make_logged_in_client()
  #  user = User.objects.get(username='test')
  #
  #  query_server = get_query_server_config()
  #
  #  db_client = HiveServerClient(query_server, user)
  #  mock_hs2_client = MockClient()
  #  setattr(db_client, '_client', mock_hs2_client)
  #
  #  # Regular session
  #  finish = desktop_conf.LDAP_PASSWORD.set_for_testing('')
  #  try:
  #    db_client.open_session(user)
  #  except:
  #    pass
  #  finally:
  #    finish()
  #    req = mock_hs2_client.open_session_args
  #    assert_equal('test', req.username)
  #    assert_equal(None, req.password)
  #    assert_equal('test', req.configuration['hive.server2.proxy.user'])
  #
  #  # LDAP credentials
  #  finish = desktop_conf.LDAP_PASSWORD.set_for_testing('I_love_Hue')
  #  try:
  #    db_client.open_session(user)
  #  except:
  #    pass
  #  finally:
  #    finish()
  #    req = mock_hs2_client.open_session_args
  #    assert_equal('test', req.username) # Same as kerberos, real username is picked from Thrift authentication, this one does not matter
  #    assert_equal(None, req.password)


def test_metastore_security():
  tmpdir = tempfile.mkdtemp()
  saved = None
  try:
    # We just replace the Beeswax conf variable
    class Getter(object):
      def get(self):
        return tmpdir

    xml = hive_site_xml(is_local=False, use_sasl=True, kerberos_principal='hive/_HOST@test.com')
    file(os.path.join(tmpdir, 'hive-site.xml'), 'w').write(xml)

    beeswax.hive_site.reset()
    saved = beeswax.conf.HIVE_CONF_DIR
    beeswax.conf.HIVE_CONF_DIR = Getter()

    metastore = get_metastore()

    assert_true(metastore['use_sasl'])
    assert_equal('thrift://darkside-1234:9999', metastore['thrift_uri'])
    assert_equal('hive/darkside-1234@test.com', metastore['kerberos_principal'])
  finally:
    beeswax.hive_site.reset()
    if saved is not None:
      beeswax.conf.HIVE_CONF_DIR = saved
    shutil.rmtree(tmpdir)


def test_close_queries_flag():
  c = make_logged_in_client()

  finish = conf.CLOSE_QUERIES.set_for_testing(False)
  try:
    resp = c.get('/beeswax/execute')
    assert_false('closeQuery()' in resp.content, resp.content)
  finally:
    finish()

  finish = conf.CLOSE_QUERIES.set_for_testing(True)
  try:
    resp = c.get('/beeswax/execute')
    assert_true('closeQuery()' in resp.content, resp.content)
  finally:
    finish()


def test_auth_pass_through():
  # Backward compatibility nothing set
  finish = []
  finish.append(LDAP_USERNAME.set_for_testing(present=False))
  finish.append(LDAP_PASSWORD.set_for_testing(present=False))

  finish.append(DEFAULT_AUTH_USERNAME.set_for_testing(present=False))
  finish.append(DEFAULT_AUTH_PASSWORD.set_for_testing(present=False))

  finish.append(AUTH_USERNAME.set_for_testing(present=False))
  finish.append(AUTH_PASSWORD.set_for_testing(present=False))
  try:
    assert_equal('hue', AUTH_USERNAME.get())
    assert_equal(None, AUTH_PASSWORD.get())
  finally:
    for f in finish:
      f()

  # Backward compatibility
  finish = []
  finish.append(LDAP_USERNAME.set_for_testing('deprecated_default_username'))
  finish.append(LDAP_PASSWORD.set_for_testing('deprecated_default_password'))

  finish.append(DEFAULT_AUTH_USERNAME.set_for_testing(present=False))
  finish.append(DEFAULT_AUTH_PASSWORD.set_for_testing(present=False))

  finish.append(AUTH_USERNAME.set_for_testing(present=False))
  finish.append(AUTH_PASSWORD.set_for_testing(present=False))
  try:
    assert_equal('deprecated_default_username', AUTH_USERNAME.get())
    assert_equal('deprecated_default_password', AUTH_PASSWORD.get())
  finally:
    for f in finish:
      f()

  # Backward compatibility override
  finish = []

  finish.append(LDAP_USERNAME.set_for_testing('deprecated_default_username'))
  finish.append(LDAP_PASSWORD.set_for_testing('deprecated_default_password'))

  finish.append(DEFAULT_AUTH_USERNAME.set_for_testing('default_username'))
  finish.append(DEFAULT_AUTH_PASSWORD.set_for_testing('default_password'))
  try:
    assert_equal('default_username', AUTH_USERNAME.get())
    assert_equal('default_password', AUTH_PASSWORD.get())
  finally:
    for f in finish:
      f()

  # HiveServer2 specific
  finish = []
  finish.append(LDAP_USERNAME.set_for_testing('deprecated_default_username'))
  finish.append(LDAP_PASSWORD.set_for_testing('deprecated_default_password'))

  finish.append(DEFAULT_AUTH_USERNAME.set_for_testing('default_username'))
  finish.append(DEFAULT_AUTH_PASSWORD.set_for_testing('default_password'))

  finish.append(AUTH_USERNAME.set_for_testing('hive_username'))
  finish.append(AUTH_PASSWORD.set_for_testing('hive_password'))
  try:
    assert_equal('hive_username', AUTH_USERNAME.get())
    assert_equal('hive_password', AUTH_PASSWORD.get())
  finally:
    for f in finish:
      f()

  # Common
  finish = []
  finish.append(LDAP_USERNAME.set_for_testing('deprecated_default_username'))
  finish.append(LDAP_PASSWORD.set_for_testing('deprecated_default_password'))

  finish.append(DEFAULT_AUTH_USERNAME.set_for_testing('default_username'))
  finish.append(DEFAULT_AUTH_PASSWORD.set_for_testing('default_password'))

  finish.append(AUTH_USERNAME.set_for_testing(present=False))
  finish.append(AUTH_PASSWORD.set_for_testing(present=False))

  try:
    assert_equal('default_username', AUTH_USERNAME.get())
    assert_equal('default_password', AUTH_PASSWORD.get())
  finally:
    for f in finish:
      f()

  # Password file specific and use common username
  finish = []
  finish.append(LDAP_USERNAME.set_for_testing('deprecated_default_username'))
  finish.append(LDAP_PASSWORD.set_for_testing('deprecated_default_password'))

  finish.append(DEFAULT_AUTH_USERNAME.set_for_testing('default_username'))
  finish.append(DEFAULT_AUTH_PASSWORD.set_for_testing(present=False))

  finish.append(AUTH_USERNAME.set_for_testing(present=False))
  finish.append(AUTH_PASSWORD.set_for_testing(present=False))
  finish.append(AUTH_PASSWORD_SCRIPT.set_for_testing('/bin/echo "my_hue_secret"'))

  try:
    assert_equal('default_username', AUTH_USERNAME.get())
    assert_equal('my_hue_secret', AUTH_PASSWORD.get())
  finally:
    for f in finish:
      f()

  # Make sure global auth password script can be used.
  finish = []
  finish.append(LDAP_USERNAME.set_for_testing('deprecated_default_username'))
  finish.append(LDAP_PASSWORD.set_for_testing('deprecated_default_password'))

  finish.append(DEFAULT_AUTH_USERNAME.set_for_testing('default_username'))
  finish.append(DEFAULT_AUTH_PASSWORD.set_for_testing(present=False))
  finish.append(DEFAULT_AUTH_PASSWORD_SCRIPT.set_for_testing('/bin/echo "my_hue_secret"'))

  finish.append(AUTH_USERNAME.set_for_testing(present=False))
  finish.append(AUTH_PASSWORD.set_for_testing(present=False))
  finish.append(AUTH_PASSWORD_SCRIPT.set_for_testing(present=False))

  try:
    assert_equal('default_username', AUTH_USERNAME.get())
    assert_equal('my_hue_secret', AUTH_PASSWORD.get())
  finally:
    for f in finish:
      f()

  # Make sure local auth password script overrides global password.
  finish = []
  finish.append(LDAP_USERNAME.set_for_testing('deprecated_default_username'))
  finish.append(LDAP_PASSWORD.set_for_testing('deprecated_default_password'))

  finish.append(DEFAULT_AUTH_USERNAME.set_for_testing('default_username'))
  finish.append(DEFAULT_AUTH_PASSWORD.set_for_testing(present=False))
  finish.append(DEFAULT_AUTH_PASSWORD_SCRIPT.set_for_testing('/bin/echo "not_my_secret"'))

  finish.append(AUTH_USERNAME.set_for_testing(present=False))
  finish.append(AUTH_PASSWORD.set_for_testing(present=False))
  finish.append(AUTH_PASSWORD_SCRIPT.set_for_testing('/bin/echo "my_hue_secret"'))

  try:
    assert_equal('default_username', AUTH_USERNAME.get())
    assert_equal('my_hue_secret', AUTH_PASSWORD.get())
  finally:
    for f in finish:
      f()


def hive_site_xml(is_local=False, use_sasl=False, thrift_uris='thrift://darkside-1234:9999',
                  warehouse_dir='/abc', kerberos_principal='test/test.com@TEST.COM',
                  hs2_kerberos_principal='hs2test/test.com@TEST.COM',
                  hs2_authentication='NOSASL', hs2_impersonation='false'):
  if not is_local:
    uris = """
       <property>
        <name>hive.metastore.uris</name>
        <value>%(thrift_uris)s</value>
      </property>
    """ % {'thrift_uris': thrift_uris}
  else:
    uris = ''

  if hs2_kerberos_principal:
    hs2_krb_princ = """
      <property>
        <name>hive.server2.authentication.kerberos.principal</name>
        <value>%(hs2_kerberos_principal)s</value>
      </property>
    """ % {'hs2_kerberos_principal': hs2_kerberos_principal}
  else:
    hs2_krb_princ = ""

  return """
    <configuration>
      %(uris)s
      <property>
        <name>hive.metastore.warehouse.dir</name>
        <value>%(warehouse_dir)s</value>
      </property>

      <property>
        <name>hive.metastore.kerberos.principal</name>
        <value>%(kerberos_principal)s</value>
      </property>

      %(hs2_krb_princ)s

      <property>
        <name>hive.server2.enable.impersonation</name>
        <value>%(hs2_impersonation)s</value>
      </property>

      <property>
        <name>hive.server2.authentication</name>
        <value>%(hs2_authentication)s</value>
      </property>

      <property>
        <name>hive.metastore.sasl.enabled</name>
        <value>%(use_sasl)s</value>
      </property>
    </configuration>
  """ % {
    'uris': uris,
    'warehouse_dir': warehouse_dir,
    'kerberos_principal': kerberos_principal,
    'hs2_krb_princ': hs2_krb_princ,
    'hs2_authentication': hs2_authentication,
    'use_sasl': str(use_sasl).lower(),
    'hs2_impersonation': hs2_impersonation,
  }


def test_ssl_cacerts():
  for desktop_kwargs, conf_kwargs, expected in [
      ({'present': False}, {'present': False}, ''),
      ({'present': False}, {'data': 'local-cacerts.pem'}, 'local-cacerts.pem'),

      ({'data': 'global-cacerts.pem'}, {'present': False}, 'global-cacerts.pem'),
      ({'data': 'global-cacerts.pem'}, {'data': 'local-cacerts.pem'}, 'local-cacerts.pem'),
      ]:
    resets = [
      desktop_conf.SSL_CACERTS.set_for_testing(**desktop_kwargs),
      conf.SSL.CACERTS.set_for_testing(**conf_kwargs),
    ]

    try:
      assert_equal(conf.SSL.CACERTS.get(), expected,
          'desktop:%s conf:%s expected:%s got:%s' % (desktop_kwargs, conf_kwargs, expected, conf.SSL.CACERTS.get()))
    finally:
      for reset in resets:
        reset()


def test_ssl_validate():
  for desktop_kwargs, conf_kwargs, expected in [
      ({'present': False}, {'present': False}, True),
      ({'present': False}, {'data': False}, False),
      ({'present': False}, {'data': True}, True),

      ({'data': False}, {'present': False}, False),
      ({'data': False}, {'data': False}, False),
      ({'data': False}, {'data': True}, True),

      ({'data': True}, {'present': False}, True),
      ({'data': True}, {'data': False}, False),
      ({'data': True}, {'data': True}, True),
      ]:
    resets = [
      desktop_conf.SSL_VALIDATE.set_for_testing(**desktop_kwargs),
      conf.SSL.VALIDATE.set_for_testing(**conf_kwargs),
    ]

    try:
      assert_equal(conf.SSL.VALIDATE.get(), expected,
          'desktop:%s conf:%s expected:%s got:%s' % (desktop_kwargs, conf_kwargs, expected, conf.SSL.VALIDATE.get()))
    finally:
      for reset in resets:
        reset()


def test_to_matching_wildcard():
    match_fn = dbms.HiveServer2Dbms.to_matching_wildcard

    assert_equal(match_fn(None), '*')
    assert_equal(match_fn(''), '*')
    assert_equal(match_fn('*'), '*')
    assert_equal(match_fn('test'), '*test*')
    assert_equal(match_fn('test*'), '*test*')


def test_apply_natural_sort():
  test_strings = ['test_1', 'test_100', 'test_2', 'test_200']
  assert_equal(apply_natural_sort(test_strings), ['test_1', 'test_2', 'test_100', 'test_200'])

  test_dicts = [{'name': 'test_1', 'comment': 'Test'},
                {'name': 'test_100', 'comment': 'Test'},
                {'name': 'test_2', 'comment': 'Test'},
                {'name': 'test_200', 'comment': 'Test'}]
  assert_equal(apply_natural_sort(test_dicts, key='name'), [{'name': 'test_1', 'comment': 'Test'},
                                                            {'name': 'test_2', 'comment': 'Test'},
                                                            {'name': 'test_100', 'comment': 'Test'},
                                                            {'name': 'test_200', 'comment': 'Test'}])

def test_hiveserver2_jdbc_url():
  hostname = socket.getfqdn()
  resets = [
    beeswax.conf.HIVE_SERVER_HOST.set_for_testing(hostname),
    beeswax.conf.HIVE_SERVER_PORT.set_for_testing('10000')
  ]
  try:
    url = hiveserver2_jdbc_url()
    assert_equal(url, 'jdbc:hive2://' + hostname + ':10000/default')

    beeswax.conf.HIVE_SERVER_HOST.set_for_testing('server-with-ssl-enabled.com')
    beeswax.conf.HIVE_SERVER_PORT.set_for_testing('10000')
    url = hiveserver2_jdbc_url()
    assert_equal(url, 'jdbc:hive2://server-with-ssl-enabled.com:10000/default')

    beeswax.hive_site.reset()
    beeswax.hive_site.get_conf()[hive_site._CNF_HIVESERVER2_USE_SSL] = 'TRUE'
    beeswax.hive_site.get_conf()[hive_site._CNF_HIVESERVER2_TRUSTSTORE_PATH] = '/path/to/truststore.jks'
    beeswax.hive_site.get_conf()[hive_site._CNF_HIVESERVER2_TRUSTSTORE_PASSWORD] = 'password'
    url = hiveserver2_jdbc_url()
    assert_equal(url, 'jdbc:hive2://server-with-ssl-enabled.com:10000/default;ssl=true;sslTrustStore=/path/to/truststore.jks;trustStorePassword=password')

    beeswax.hive_site.reset()
    beeswax.hive_site.get_conf()[hive_site._CNF_HIVESERVER2_USE_SSL] = 'TRUE'
    hadoop.ssl_client_site.reset()
    hadoop.ssl_client_site.get_conf()[ssl_client_site._CNF_TRUSTORE_LOCATION] = '/etc/ssl-conf/CA_STANDARD/truststore.jks'
    url = hiveserver2_jdbc_url() # Pick-up trustore from ssl-client.xml
    assert_equal(url, 'jdbc:hive2://server-with-ssl-enabled.com:10000/default;ssl=true;sslTrustStore=/etc/ssl-conf/CA_STANDARD/truststore.jks')

    beeswax.hive_site.get_conf()[hive_site._CNF_HIVESERVER2_USE_SSL] = 'FALSE'
    url = hiveserver2_jdbc_url()
    assert_equal(url, 'jdbc:hive2://server-with-ssl-enabled.com:10000/default')
  finally:
    beeswax.hive_site.reset()
    hadoop.ssl_client_site.reset()
    for reset in resets:
        reset()

def test_sasl_auth_in_large_download():
  db = None
  failed = False
  max_rows = 10000

  if hive_site.get_hiveserver2_thrift_sasl_qop() != "auth-conf" or \
     hive_site.get_hiveserver2_authentication() != 'KERBEROS':
    raise SkipTest

  client = make_logged_in_client(username="systest", groupname="systest", recreate=False, is_superuser=False)
  user = User.objects.get(username='systest')
  add_to_group('systest')
  grant_access("systest", "systest", "beeswax")

  desktop_conf.SASL_MAX_BUFFER.set_for_testing(2*1024*1024)

  # Create a big table
  table_info = {'db': 'default', 'table_name': 'dummy_'+random_generator().lower()}
  drop_sql = "DROP TABLE IF EXISTS %(db)s.%(table_name)s" % table_info
  create_sql = "CREATE TABLE IF NOT EXISTS %(db)s.%(table_name)s (w0 CHAR(8),w1 CHAR(8),w2 CHAR(8),w3 CHAR(8),w4 CHAR(8),w5 CHAR(8),w6 CHAR(8),w7 CHAR(8),w8 CHAR(8),w9 CHAR(8))" % table_info
  hql = string_io()
  hql.write("INSERT INTO %(db)s.%(table_name)s VALUES " % (table_info))
  for i in range(max_rows-1):
    w = random_generator(size=7)
    hql.write("('%s0','%s1','%s2','%s3','%s4','%s5','%s6','%s7','%s8','%s9')," % (w,w,w,w,w,w,w,w,w,w))
  w = random_generator(size=7)
  hql.write("('%s0','%s1','%s2','%s3','%s4','%s5','%s6','%s7','%s8','%s9')" % (w,w,w,w,w,w,w,w,w,w))

  try:
    db = dbms.get(user, get_query_server_config())
    db.use(table_info['db'])
    query = hql_query(drop_sql)
    handle = db.execute_and_wait(query, timeout_sec=120)
    query = hql_query(create_sql)
    handle = db.execute_and_wait(query, timeout_sec=120)
    query = hql_query(hql.getvalue())
    handle = db.execute_and_wait(query, timeout_sec=300)
    hql.close()
  except Exception as ex:
    failed = True

  # Big table creation (data upload) is successful
  assert_false(failed)

  # Fetch large data set
  hql = "SELECT w0,w1,w2,w3,w4,w5,w6,w7,w8,w9,w0,w1,w2,w3,w4,w5,w6,w7,w8,w9 FROM %(db)s.%(table_name)s" % table_info

  # large rows
  max_rows = 8745

  try:
    query = hql_query(hql)
    handle = db.execute_and_wait(query)
    results = db.fetch(handle, True, max_rows-20)
  except QueryServerException as ex:
    if 'Invalid OperationHandle' in ex.message and 'EXECUTE_STATEMENT' in ex.message:
      failed = True
  except:
      failed = True

  # Fetch large data set is successful because SASL_MAX_BUFFER > RESULT_DATA
  assert_false(failed)

  # Test case when SASL_MAX_BUFFER < RESULT_DATA
  try:
    query = hql_query(hql)
    handle = db.execute_and_wait(query)
    results = db.fetch(handle, True, max_rows)
  except QueryServerException as ex:
    if 'Invalid OperationHandle' in ex.message and 'EXECUTE_STATEMENT' in ex.message:
      failed = True
  except:
      failed = True

  # Fetch large data set fails because SASL_MAX_BUFFER < RESULT_DATA In your log file you will see following log lines
  # thrift_util  INFO     Thrift exception; retrying: Error in sasl_decode (-1) SASL(-1): generic failure: Unable to find a callback: 32775
  # thrift_util  INFO     Increase the SASL_MAX_BUFFER value in hue.ini
  assert_true(failed)
  failed = False

  # Cleanup
  hql = "DROP TABLE %(db)s.%(table_name)s" % table_info

  try:
    query = hql_query(hql)
    handle = db.execute_and_wait(query)
  except QueryServerException as ex:
    if 'Invalid OperationHandle' in ex.message and 'EXECUTE_STATEMENT' in ex.message:
      failed = True
  except:
      failed = True
  assert_false(failed)
