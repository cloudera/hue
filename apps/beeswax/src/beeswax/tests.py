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

import cStringIO
import gzip
import json
import logging
import os
import re
import shutil
import socket
import tablib
import tempfile
import threading

import hadoop

from nose.tools import assert_true, assert_equal, assert_false, assert_not_equal, assert_raises
from nose.plugins.skip import SkipTest

from django.utils.encoding import smart_str
from django.utils.html import escape
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from desktop.lib.django_test_util import make_logged_in_client, assert_equal_mod_whitespace
from desktop.lib.test_utils import grant_access, add_to_group
from desktop.lib.security_util import get_localhost_name

import desktop.conf as desktop_conf

import beeswax.create_table
import beeswax.hive_site
import beeswax.models
import beeswax.views

from beeswax import conf, hive_site
from beeswax.conf import HIVE_SERVER_HOST
from beeswax.views import collapse_whitespace, _save_design
from beeswax.test_base import make_query, wait_for_query_to_finish, verify_history, get_query_server_config,\
  HIVE_SERVER_TEST_PORT, fetch_query_result_data
from beeswax.design import hql_query, strip_trailing_semicolon
from beeswax.data_export import upload, download
from beeswax.models import SavedQuery, QueryHistory, HQL
from beeswax.server import dbms
from beeswax.server.dbms import QueryServerException
from beeswax.server.hive_server2_lib import HiveServerClient,\
  PartitionValueCompatible, HiveServerTable
from beeswax.test_base import BeeswaxSampleProvider
from beeswax.hive_site import get_metastore

from desktop.lib.exceptions_renderable import PopupException
from desktop.conf import LDAP_USERNAME, LDAP_PASSWORD


LOG = logging.getLogger(__name__)

def _make_query(client, query, submission_type="Execute",
                udfs=None, settings=None, resources=[],
                wait=False, name=None, desc=None, local=True,
                is_parameterized=True, max=30.0, database='default', email_notify=False, params=None, **kwargs):

  res = make_query(client, query, submission_type,
                   udfs, settings, resources,
                   wait, name, desc, local, is_parameterized, max, database, email_notify, params, **kwargs)

  # Should be in the history if it's submitted.
  if submission_type == 'Execute':
    fragment = collapse_whitespace(smart_str(escape(query[:20])))
    verify_history(client, fragment=fragment)

  return res


def get_csv(client, result_response):
  """Get the csv for a query result"""
  content = json.loads(result_response.content)
  assert_true(content['isSuccess'])
  csv_link = '/beeswax/download/%s/csv' % content['id']
  return client.get(csv_link).content


class TestBeeswaxWithHadoop(BeeswaxSampleProvider):
  requires_hadoop = True

  def setUp(self):
    self.user = User.objects.get(username='test')
    add_to_group('test')
    self.db = dbms.get(self.user, get_query_server_config())

  def _verify_query_state(self, state):
    """
    Verify the state of the latest query.
    Return the id of that query
    """
    resp = self.client.get('/beeswax/query_history')
    history = resp.context['page'].object_list[0]
    last_state = history.last_state
    assert_equal(beeswax.models.QueryHistory.STATE[last_state], state)
    return history.id

  def test_query_with_error(self):
    # Creating a table "again" should not work; error should be displayed.
    response = _make_query(self.client, "CREATE TABLE test (foo INT)", wait=True)
    content = json.loads(response.content)
    assert_true("AlreadyExistsException" in content.get('message'), content)

  def test_configuration(self):
    # No HS2 API
    raise SkipTest

    params = {'server': 'default'}

    response = self.client.post("/beeswax/configuration", params)
    response_verbose = self.client.post("/beeswax/configuration?include_hadoop=true", params)

    assert_true("hive.exec.scratchdir" in response.content)
    assert_true("hive.exec.scratchdir" in response_verbose.content)

    assert_true("javax.jdo.option.ConnectionPassword**********" in response_verbose.content)
    assert_true("javax.jdo.option.ConnectionPassword**********" in response_verbose.content)

    assert_false("tasktracker.http.threads" in response.content)
    assert_true("tasktracker.http.threads" in response_verbose.content)
    assert_true("A base for other temporary directories" in response_verbose.content)

  def test_query_with_resource(self):
    script = self.cluster.fs.open("/square.py", "w")
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
      resources=[("FILE", "/square.py")], local=False)
    response = wait_for_query_to_finish(self.client, response, max=180.0)
    content = fetch_query_result_data(self.client, response)
    assert_equal([['0'], ['1'], ['4'], ['9']], content["results"][0:4])

  def test_query_with_setting(self):
    response = _make_query(self.client, "CREATE TABLE test2 AS SELECT foo+1 FROM test WHERE foo=4",
      settings=[("mapred.job.name", "test_query_with_setting"),
        ("hive.exec.compress.output", "true")], local=False) # Run on MR, because that's how we check it worked.
    response = wait_for_query_to_finish(self.client, response, max=180.0)
    # Check that we actually got a compressed output
    files = self.cluster.fs.listdir("/user/hive/warehouse/test2")
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
    wait_for_query_to_finish(self.client, _make_query(self.client, QUERY, local=False), max=180.0)
    self._verify_query_state(beeswax.models.QueryHistory.STATE.available)

    # Make sure expired query states are lazily updated.
    resp = self.client.get('/beeswax/query_history')
    history = resp.context['page'].object_list[0]
    self.db.close_operation(history.get_full_object().get_handle())
    resp = self.client.get("/beeswax/execute/query/%s" % history.id)
    assert_true(resp.status_code, 302)

    resp = self.client.get('/beeswax/query_history')
    history = resp.context['page'].object_list[0]
    assert_equal(beeswax.models.QueryHistory.STATE[history.last_state], beeswax.models.QueryHistory.STATE.expired)


  def test_basic_flow(self):
    # Minimal server operation
    assert_equal(['default', 'other_db'], self.db.get_databases())

    # Query the data
    # We use a semicolon here for kicks; the code strips it out.
    QUERY = """
      SELECT MIN(foo), MAX(foo), SUM(foo) FROM test;
    """
    response = _make_query(self.client, QUERY, local=False)
    content = json.loads(response.content)
    assert_true('watch_url' in content)
    # Check that we report this query as "running". (This query takes a while.)
    self._verify_query_state(beeswax.models.QueryHistory.STATE.running)

    response = wait_for_query_to_finish(self.client, response, max=180.0)
    content = fetch_query_result_data(self.client, response)

    assert_equal([0, 255, 32640], content["results"][0], content)
    assert_equal(['INT_TYPE', 'INT_TYPE', 'BIGINT_TYPE'], [col['type'] for col in content["columns"]])
    assert_equal(1, len(content["hadoop_jobs"]), content) # Should be 1 after HS2 bug is fixed
    self._verify_query_state(beeswax.models.QueryHistory.STATE.available)

    # Query multi-page request
    QUERY = """
      SELECT * FROM test
    """
    response = _make_query(self.client, QUERY, name='select star', local=False)
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
    assert_equal(257, response.content.count("\n"))

  def test_result_escaping(self):
    # Check for XSS and NULL display
    QUERY = """
      SELECT 'abc', 1.0, 1=1, 1, 1/0, '<a>lala</a>lulu', 'some   spaces' from test LIMIT 3;
    """
    response = _make_query(self.client, QUERY, local=False)
    content = json.loads(response.content)
    assert_true('watch_url' in content)

    response = wait_for_query_to_finish(self.client, response, max=180.0)
    content = fetch_query_result_data(self.client, response)

    assert_equal([
        [u'abc', 1.0, True, 1, u'NULL', u'&lt;a&gt;lala&lt;/a&gt;lulu', 'some&nbsp;&nbsp;&nbsp;spaces'],
        [u'abc', 1.0, True, 1, u'NULL', u'&lt;a&gt;lala&lt;/a&gt;lulu', 'some&nbsp;&nbsp;&nbsp;spaces'],
        [u'abc', 1.0, True, 1, u'NULL', u'&lt;a&gt;lala&lt;/a&gt;lulu', 'some&nbsp;&nbsp;&nbsp;spaces'],
      ], content["results"], content)

  def test_query_with_udf(self):
    """
    Testing query with udf
    """
    response = _make_query(self.client, "SELECT my_sqrt(foo), my_float(foo) FROM test WHERE foo=4",
      udfs=[('my_sqrt', 'org.apache.hadoop.hive.ql.udf.UDFSqrt'),
            ('my_float', 'org.apache.hadoop.hive.ql.udf.UDFToFloat')], local=False)
    response = wait_for_query_to_finish(self.client, response, max=60.0)
    content = fetch_query_result_data(self.client, response)

    assert_equal([2.0, 4.0], content["results"][0])
    log = content['log']
    assert_true(search_log_line('parse.SemanticAnalyzer', 'Completed plan generation', log), log)
    assert_true(search_log_line('ql.Driver', 'Semantic Analysis Completed', log), log)
    assert_true(search_log_line('exec.Task', '100%', log), log)
    assert_true(search_log_line('ql.Driver', 'OK', log), log)
    # Test job extraction while we're at it
    assert_equal(1, len(content["hadoop_jobs"]), "Should have started 1 job and extracted it.")

  def test_query_with_remote_udf(self):
    """
    UDF is on HDFS.  This was implemented as part of HIVE-1157.
    """
    # Can't figure out what's going wrong right now :(
    raise SkipTest

    src = file(os.path.join(os.path.dirname(__file__), "..", "..", "java-lib", "BeeswaxTest.jar"))
    dest = self.cluster.fs.open("/tmp/hive1157.jar", "w")
    shutil.copyfileobj(src, dest)
    dest.close()
    src.close()

    # Beware that this doesn't work with mapred.job.tracker=local :/
    response = _make_query(self.client, "SELECT cube(foo) FROM test WHERE foo=4",
      udfs=[('cube', 'com.cloudera.beeswax.CubeSampleUDF')],
      resources=[('JAR', '/tmp/hive1157.jar')], local=False)
    response = wait_for_query_to_finish(self.client, response, max=60.0)
    assert_equal(["64"], response.context["results"][0])

  def test_query_with_simple_errors(self):
    hql = "SELECT KITTENS ARE TASTY"
    resp = _make_query(self.client, hql, name='tasty kittens', wait=False, local=False)
    assert_true("ParseException line" in json.loads(resp.content)["message"])

    # Watch page will fail as operationHandle=None
    query_id = self._verify_query_state(beeswax.models.QueryHistory.STATE.failed)

  def test_sync_query_exec(self):
    # Execute Query Synchronously, set fetch size and fetch results
    # verify the size of resultset,
    hql = """
      SELECT foo FROM test;
    """
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
      SELECT FROM zzzzz
    """
    query = hql_query(hql)
    try:
      self.db.execute_and_wait(query)
    except QueryServerException, bex:
      assert_equal(bex.errorCode, 40000)
      assert_equal(bex.SQLState, "42000")

  def test_fetch_configuration(self):
    class MockClient:
      """Check if sent fetch correctly supports start_over."""
      def __init__(self, support_start_over):
        self.support_start_over = support_start_over

      def fetch(self, query_id, start_over, fetch_size):
        assert_equal(self.support_start_over, start_over)
        class Result: pass
        res = Result()
        res.ready = False
        return res

    class ConfigVariable:
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
    response = _make_query(self.client, "SELECT foo FROM test WHERE foo='$x' and bar='$y'", is_parameterized=False)
    content = json.loads(response.content)
    # Assert no parameterization was offered
    assert_true('watch_url' in content, content)

    data = {
      'query-query': "SELECT foo FROM test WHERE foo='$x' and bar='$y'",
      'query-database': "default"
    }
    response = self.client.post(reverse('beeswax:api_parameters'), data)
    content = json.loads(response.content)
    assert_equal([
        {'parameter': 'parameterization-x', 'name': 'x'},
        {'parameter': 'parameterization-y', 'name': 'y'}
      ], content['parameters'], content)

    # Now fill it out
    response = _make_query(self.client, "SELECT foo FROM test WHERE foo='$x' and bar='$y'", params=[('x', '1'), ('y', '2')])
    content = json.loads(response.content)
    assert_true('watch_url' in content, content)
    query_history = QueryHistory.get(content['id'])

    # Check that substitution happened!
    assert_equal("SELECT foo FROM test WHERE foo='1' and bar='2'", query_history.query)

    # Check that error handling is reasonable
    response = _make_query(self.client, "SELECT foo FROM test WHERE foo='$x' and bar='$y'", params=[('x', "'_this_is_not SQL "), ('y', '2')])
    content = json.loads(response.content)
    assert_true("FAILED: ParseException" in content.get('message'), content)

    # Check multi DB with a non default DB
    response = _make_query(self.client, "CREATE TABLE test (foo INT, bar STRING)", database='other_db')
    response = wait_for_query_to_finish(self.client, response)
    response = _make_query(self.client, "SELECT foo FROM test WHERE foo='$x' and bar='$y'", database='other_db')

    response = _make_query(self.client, "SELECT foo FROM test WHERE foo='$x' and bar='$y'", database='other_db',
                           params=[('x', '1'), ('y', '2')])
    content = json.loads(response.content)
    assert_true('watch_url' in content, content)
    query_history = QueryHistory.get(content['id'])
    assert_equal('other_db', query_history.design.get_design().query['database'])

  def test_explain_query(self):
    c = self.client
    response = _make_query(c, "SELECT KITTENS ARE TASTY", submission_type="Explain")
    assert_true("ParseException line" in json.loads(response.content)["message"])
    CREATE_TABLE = "CREATE TABLE test_explain (foo INT, bar STRING);"
    response = _make_query(c, CREATE_TABLE)
    wait_for_query_to_finish(c, response)

    response = _make_query(c, "SELECT SUM(foo) FROM test_explain", submission_type="Explain")
    explanation = json.loads(response.content)['explanation']
    assert_true('ABSTRACT SYNTAX TREE' in explanation, explanation)

  def test_explain_query_i18n(self):
    query = u"SELECT foo FROM test_utf8 WHERE bar='%s'" % (unichr(200),)
    response = _make_query(self.client, query, submission_type="Explain")
    explanation = json.loads(response.content)['explanation']
    assert_true('ABSTRACT SYNTAX TREE' in explanation, explanation)

  def test_query_i18n(self):
    # Test fails because HIVE_PLAN cannot be found and raises FileNotFoundException
    # because of a Hive bug.
    raise SkipTest

    # Selecting from utf-8 table should get correct result
    query = u"SELECT * FROM test_utf8 WHERE bar='%s'" % (unichr(200),)
    response = _make_query(self.client, query, wait=True)
    assert_equal(["200", unichr(200)], response.context["results"][0], "selecting from utf-8 table should get correct result")

    csv = get_csv(self.client, response)
    assert_equal('"200","%s"' % (unichr(200).encode('utf-8'),), csv.split()[1])

    # Selecting from latin1 table should not blow up
    query = u"SELECT * FROM test_latin1 WHERE bar='%s'" % (unichr(200),)
    response = _make_query(self.client, query, wait=True)
    assert_true('results' in response.context, "selecting from latin1 table should not blow up")

    # Describe table should be fine with non-ascii comment
    response = self.client.get('/beeswax/table/default/test_utf8')
    assert_equal(response.context['table'].parameters['comment'], self.get_i18n_table_comment())

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
    except:
      LOG.exception("Saw exception in child thread.")

  def test_multiple_statements_no_result_set(self):
    hql = """
      CREATE TABLE test_multiple_statements_1 (a int);
      CREATE TABLE test_multiple_statements_2 (a int);
      DROP TABLE test_multiple_statements_1;
      DROP TABLE test_multiple_statements_2;
    """

    resp = _make_query(self.client, hql)
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

    resp = _make_query(self.client, hql)

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

    resp = _make_query(self.client, hql)

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

    resp = _make_query(self.client, hql)

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

  def test_multiple_statements_with_error(self):
    hql = """
      show tables;
      select * from
    """

    resp = _make_query(self.client, hql)

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

    for i in range(PARALLEL_TASKS):
      csv = get_csv(self.client, responses[i])
      # We get 3 rows: Column header, and 2 rows of results in double quotes
      answer = [ int(data.strip('"')) for data in csv.split()[1:] ]
      assert_equal( [ i + 1, i + 2 ], answer)

  def test_data_export_limit_clause(self):
    limit = 3
    hql = 'SELECT foo FROM test limit %d' % (limit,)
    query = hql_query(hql)

    handle = self.db.execute_and_wait(query)
    # Get the result in csv. Should have 3 + 1 header row.
    csv_resp = download(handle, 'csv', self.db)
    assert_equal(len(csv_resp.content.strip().split('\n')), limit + 1)

  def test_query_done_cb(self):
    hql = 'SELECT * FROM test'
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
    hql = 'SELECT * FROM test'
    query = hql_query(hql)
    dataset = tablib.Dataset()

    # Get the result in xls.

    handle = self.db.execute_and_wait(query)
    xls_resp = download(handle, 'xls', self.db)

    dataset.xls = xls_resp.content
    # It should have 257 lines (256 + header)
    assert_equal(len(dataset.csv.strip('\r\n').split('\r\n')), 257, dataset.csv)

    # Get the result in csv.
    query = hql_query(hql)
    handle = self.db.execute_and_wait(query)
    csv_resp = download(handle, 'csv', self.db)
    assert_equal(csv_resp.content.replace('.0', ''), dataset.csv.replace('.0', ''))

  def test_data_upload(self):
    hql = 'SELECT * FROM test'
    query = hql_query(hql)

    handle = self.db.execute_and_wait(query)
    upload('/tmp/test_data_upload.csv', handle, self.user, self.db, self.cluster.fs)

    assert_true(self.cluster.fs.exists('/tmp/test_data_upload.csv'))

  def test_designs(self):
    cli = self.client

    # An auto hql design should be created, and it should ignore the given name and desc
    _make_query(self.client, 'SELECT bogus FROM test', name='mydesign', desc='hyatt')
    resp = cli.get('/beeswax/list_designs')
    n_designs = len(resp.context['page'].object_list)

    # Retrieve that design. It's the first one since it's most recent
    design = beeswax.models.SavedQuery.objects.all()[0]
    resp = cli.get('/beeswax/execute/design/%s' % design.id)
    assert_true('query' in resp.context, resp.context)
    assert_true(resp.context['query'] is None, resp.context)
    assert_equal(design, resp.context['design'], resp.context)

    # Retrieve that query history. It's the first one since it's most recent
    query_history = beeswax.models.QueryHistory.objects.all()[0]
    resp = cli.get('/beeswax/execute/query/%s' % query_history.id)
    assert_true('query' in resp.context, resp.context)
    assert_true(resp.context['query'] is not None, resp.context)
    assert_true('design' in resp.context, resp.context)
    assert_true(resp.context['design'] is not None, resp.context)

    resp = cli.get(reverse('beeswax:api_fetch_saved_design', kwargs={'design_id': design.id}))
    content = json.loads(resp.content)
    assert_true('SELECT bogus FROM test' in content['design']['query'], content)

    # Make a valid auto hql design
    resp = _make_query(self.client, 'SELECT * FROM test')
    wait_for_query_to_finish(self.client, resp, max=60.0)

    resp = cli.get('/beeswax/list_designs')
    nplus_designs = len(resp.context['page'].object_list)
    assert_true(nplus_designs == n_designs, 'Auto design should not show up in list_designs')

    # Test explicit save and use another DB
    query = 'MORE BOGUS JUNKS FROM test'
    resp = _make_query(self.client, query, name='rubbish', submission_type='Save', database='other_db')
    content = json.loads(resp.content)
    assert_equal(0, content['status'])
    assert_true('design_id' in content, content)

    resp = cli.get('/beeswax/list_designs')
    assert_true('rubbish' in resp.content, resp.content)
    nplusplus_designs = len(resp.context['page'].object_list)
    assert_true(nplusplus_designs > nplus_designs)

    # Retrieve that design and check correct DB is selected
    design = beeswax.models.SavedQuery.objects.filter(name='rubbish')[0]
    resp = cli.get(reverse('beeswax:api_fetch_saved_design', kwargs={'design_id': design.id}))
    content = json.loads(resp.content)
    assert_true(query in content['design']['query'], content)
    assert_equal('', content['design']['desc'], content)
    assert_equal('other_db', content['design']['database'], content)

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
    resp = cli.post('/beeswax/delete_designs', {u'designs_selection': [u'1']})
    assert_equal(resp.status_code, 302)

    # Delete designs
    design_ids = map(str, designs.values_list('id', flat=True))
    resp = cli.get('/beeswax/delete_designs', {u'designs_selection': design_ids})
    assert_true('Delete design(s)' in resp.content, resp.content)
    resp = cli.post('/beeswax/delete_designs', {u'designs_selection': design_ids})
    assert_equal(resp.status_code, 302)

    # Helper to test the view, filtering, etc
    def do_view(param):
      resp = cli.get('/beeswax/list_designs?' + param)
      assert_true(len(resp.context['page'].object_list) >= 0)     # Make the query run
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
    _make_query(self.client, "select noHQL", name='my rubbish kuery', submission_type='Save')
    # Run something
    _make_query(self.client, "Even More Bogus Junk")
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
        resp = wait_for_query_to_finish(self.client, resp, max=60)
        resp.success_url = success_url # Hack until better API

      # Check that data is right
      if verify:
        target_ls = self.cluster.fs.listdir(target_dir)
        assert_true(len(target_ls) >= 1)
        data_buf = ""


        assert_equal(len(target_ls), 1)

        for target in target_ls:
          target_file = self.cluster.fs.open(target_dir + '/' + target)
          data_buf += target_file.read()
          target_file.close()

        assert_equal(256, len(data_buf.strip().split('\n')))
        assert_true('255' in data_buf)

      return resp

    TARGET_DIR_ROOT = '/tmp/beeswax.test_save_directory_results'

    # Already existing dir
    if not self.cluster.fs.exists(TARGET_DIR_ROOT):
      self.cluster.fs.mkdir(TARGET_DIR_ROOT)
      self.cluster.fs.chown(TARGET_DIR_ROOT, user='test')
    hql = "SELECT * FROM test"
    resp = _make_query(self.client, hql, wait=True, local=False, max=180.0)
    resp = save_and_verify(resp, TARGET_DIR_ROOT, verify=False)
    assert_true('Directory already exists' in resp.content, resp.content)

    # SELECT *. (Result dir is same as table dir.)
    hql = "SELECT * FROM test"
    resp = _make_query(self.client, hql, wait=True, local=False, max=180.0)
    resp = save_and_verify(resp, TARGET_DIR_ROOT + '/1', verify=False)
    resp = self.client.get(resp.success_url)
    # Success and went to FB
    assert_true('File Browser' in resp.content, resp.content)

    # SELECT columns. (Result dir is in /tmp.)
    hql = "SELECT foo, bar FROM test"
    resp = _make_query(self.client, hql, wait=True, local=False, max=180.0)
    resp = save_and_verify(resp, TARGET_DIR_ROOT + '/2')
    resp = self.client.get(resp.success_url)
    assert_true('File Browser' in resp.content, resp.content)

    # Partition tables
    hql = "SELECT * FROM test_partitions"
    resp = _make_query(self.client, hql, wait=True, local=False, max=180.0)
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

    TARGET_FILE = '/tmp/beeswax.test_save_file_results'
    if self.cluster.fs.exists(TARGET_FILE):
      self.cluster.fs.rmtree(TARGET_FILE)

    # SELECT columns. (Result dir is in /tmp.)
    hql = "SELECT foo, bar FROM test"
    resp = _make_query(self.client, hql, wait=True, local=False, max=180.0)
    resp = save_and_verify(resp, TARGET_FILE)
    resp = self.client.get(resp.success_url)
    assert_true('File Browser' in resp.content, resp.content)

    # overwrite = false
    hql = "SELECT foo, bar FROM test"
    resp = _make_query(self.client, hql, wait=True, local=False, max=180.0)
    resp = save_and_verify(resp, TARGET_FILE, overwrite=False, verify=False)
    assert_true('-3' in resp.content)
    assert_true('already exists' in resp.content)

    # Partition tables
    hql = "SELECT * FROM test_partitions"
    resp = _make_query(self.client, hql, wait=True, local=False, max=180.0)
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
      resp = _make_query(self.client, 'SELECT * FROM %s' % target_tbl, wait=True, local=False)
      content = fetch_query_result_data(self.client, resp)
      for i in xrange(90):
        assert_equal([i, '0x%x' % (i,)], content['results'][i])

    TARGET_TBL_ROOT = 'test_copy'

    # SELECT *. (Result dir is same as table dir.)
    hql = "SELECT * FROM test"
    resp = _make_query(self.client, hql, wait=True, local=False, max=180.0)
    save_and_verify(resp, TARGET_TBL_ROOT + '_1')

    # SELECT columns. (Result dir is in /tmp.)
    hql = "SELECT foo, bar FROM test"
    resp = _make_query(self.client, hql, wait=True, local=False, max=180.0)
    save_and_verify(resp, TARGET_TBL_ROOT + '_2')

    # Save to another DB
    hql = "SELECT * FROM test"
    resp = _make_query(self.client, hql, wait=True, local=False, max=180.0)
    save_and_verify(resp, 'other_db.' + TARGET_TBL_ROOT)

  def test_install_examples(self):
    assert_true(not beeswax.models.MetaInstall.get().installed_example)

    # Check popup
    resp = self.client.get('/beeswax/install_examples')
    assert_true('POST request is required.' in json.loads(resp.content)['message'])

    self.client.post('/beeswax/install_examples')

    # New tables exists
    resp = self.client.get('/metastore/tables/')
    assert_true('sample_08' in resp.content)
    assert_true('sample_07' in resp.content)

    # New designs exists
    resp = self.client.get('/beeswax/list_designs')
    assert_true('Sample: Job loss' in resp.content, resp.content)
    assert_true('Sample: Salary growth' in resp.content)
    assert_true('Sample: Top salary' in resp.content)

    # Now install it a second time, and no error
    resp = self.client.post('/beeswax/install_examples')
    assert_equal(0, json.loads(resp.content)['status'])
    assert_equal('', json.loads(resp.content)['message'])


  def test_create_table_generation(self):
    """
    Checks HQL generation for create table.

    NOT TESTED/DONE: Validation checks for the inputs.
    """
    # Make sure we get a form
    resp = self.client.get("/beeswax/create/create_table/default")
    assert_true("Field terminator" in resp.content)
    # Make a submission
    resp = self.client.post("/beeswax/create/create_table/default", {
      'table-name': 'my_table',
      'table-comment': 'Yo>>>>dude',  # Make sure escaping is sort of ok.
      'table-row_format': 'Delimited',
      'table-field_terminator_0': r',',
      'table-collection_terminator_0': r'\002',
      'table-map_key_terminator_0': r'\003',
      'table-file_format': 'TextFile',
      'table-use_default_location': 'False',
      'table-external_location': '/tmp/foo',
      'columns-0-column_name': 'my_col',
      'columns-0-column_type': 'string',
      'columns-0-_exists': 'True',
      'columns-next_form_id': '1',
      'partitions-next_form_id': '0',
      'create': 'Create table',
    }, follow=True)

    # Ensure we can see table.
    response = self.client.get("/metastore/table/default/my_table")
    assert_true("my_col" in response.content)


  def test_create_table_timestamp(self):
    # Check form
    response = self.client.get('/beeswax/create/create_table/default')
    assert_true('<option value="timestamp">timestamp</option>' in response.content, response.content)

    # Check creation
    filename = '/tmp/timestamp_data'

    # Bad format
    self._make_custom_data_file(filename, [0, 0, 0])
    self._make_table('timestamp_invalid_data', 'CREATE TABLE timestamp_invalid_data (timestamp1 TIMESTAMP)', filename)

    response = self.client.get("/metastore/table/default/timestamp_invalid_data")
    assert_true('NULL' in response.content, response.content)

    # Good format
    self._make_custom_data_file(filename, ['2012-01-01 10:11:30', '2012-01-01 10:11:31'])
    self._make_table('timestamp_valid_data', 'CREATE TABLE timestamp_valid_data (timestamp1 TIMESTAMP)', filename)

    response = self.client.get("/metastore/table/default/timestamp_valid_data")
    assert_true('2012-01-01&nbsp;10:11:30' in response.content, response.content)

  def test_partitioned_create_table(self):
    # Make sure we get a form
    resp = self.client.get("/beeswax/create/create_table/default")
    assert_true("Field terminator" in resp.content)
    # Make a submission
    resp = self.client.post("/beeswax/create/create_table/default", {
      'table-name': 'my_table2',
      'table-row_format': 'Delimited',
      'table-field_terminator_0': r'\001',
      'table-collection_terminator_0': r'\002',
      'table-map_key_terminator_0': r'\003',
      'table-file_format': 'TextFile',
      'table-use_default_location': 'True',
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

#response = wait_for_query_to_finish(self.client, response)
    assert_equal_mod_whitespace("""
        CREATE TABLE `default.my_table2`
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
    """, history.query)


  def test_create_table_dependencies(self):
    """
    Test field dependency in the create table form
    """
    resp = self.client.post("/beeswax/create/create_table/default", {
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
    assert_true(resp.context["table_form"].errors["input_format_class"])
    assert_true(resp.context["table_form"].errors["output_format_class"])
    assert_true(resp.context["table_form"].errors["serde_name"])
    assert_true(resp.context["table_form"].errors["serde_properties"])
    assert_true(resp.context["table_form"].errors["serde_properties"])

    assert_true(resp.context["columns_form"].forms[0].errors["map_key_type"])
    assert_true(resp.context["columns_form"].forms[0].errors["map_value_type"])


  def test_create_table_import(self):
    """Test create table wizard"""
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
        sio = cStringIO.StringIO()
        gzdat = gzip.GzipFile(fileobj=sio, mode='wb')
        gzdat.write(data)
        gzdat.close()
        data = sio.getvalue()

      f = self.cluster.fs.open(filename, "w")
      f.write(data)
      f.close()
      self.cluster.fs.do_as_superuser(self.cluster.fs.chown, filename, 'test', 'test')

    self.cluster.fs.do_as_user('test', self.cluster.fs.create_home_dir, '/user/test')

    write_file('/tmp/spacé.dat'.decode('utf-8'), RAW_FIELDS, ' ')
    write_file('/tmp/tab.dat', RAW_FIELDS, '\t')
    write_file('/tmp/comma.dat', RAW_FIELDS, ',')
    write_file('/tmp/pipes.dat', RAW_FIELDS, '|')
    write_file('/tmp/comma.dat.gz', RAW_FIELDS, ',', do_gzip=True)
    write_file('/tmp/comma.csv', CSV_FIELDS, ',')

    # Test auto delim selection
    resp = self.client.post('/beeswax/create/import_wizard/default', {
      'submit_file': 'on',
      'path': '/tmp/comma.dat',
      'name': 'test_create_import',
    })
    assert_equal(resp.context['fields_list'], RAW_FIELDS)

    # Test same with gzip
    resp = self.client.post('/beeswax/create/import_wizard/default', {
      'submit_file': 'on',
      'path': '/tmp/comma.dat.gz',
      'name': 'test_create_import',
    })
    assert_equal(resp.context['fields_list'], RAW_FIELDS)

    # Make sure space works
    resp = self.client.post('/beeswax/create/import_wizard/default', {
      'submit_preview': 'on',
      'path': '/tmp/spacé.dat',
      'name': 'test_create_import',
      'delimiter_0': ' ',
      'delimiter_1': '',
      'file_type': 'text',
    })
    assert_equal(len(resp.context['fields_list'][0]), 4)

    # Make sure custom delimiters work
    resp = self.client.post('/beeswax/create/import_wizard/default', {
      'submit_preview': 'on',
      'path': '/tmp/pipes.dat',
      'name': 'test_create_import',
      'delimiter_0': '__other__',
      'delimiter_1': '|',
      'file_type': 'text',
    })
    assert_equal(len(resp.context['fields_list'][0]), 3)

    # Make sure quoted CSV works
    resp = self.client.post('/beeswax/create/import_wizard/default', {
      'submit_preview': 'on',
      'path': '/tmp/comma.csv',
      'name': 'test_create_import_csv',
      'delimiter_0': '__other__',
      'delimiter_1': ',',
      'file_type': 'text',
    })
    assert_equal(resp.context['fields_list'], [
      ['a', 'b', 'c'],
      ['a,a', 'b,b', 'c,c'],
      ['a,"a', 'b,"b', 'c,"c'],
    ] )

    # Test column definition
    resp = self.client.post('/beeswax/create/import_wizard/default', {
      'submit_delim': 'on',
      'path': '/tmp/comma.dat.gz',
      'name': 'test_create_import',
      'delimiter_0': ',',
      'delimiter_1': '',
      'file_type': 'gzip',
    })
    # Should have 3 columns available
    assert_equal(len(resp.context['column_formset'].forms), 3)

    # Test table creation and data loading
    resp = self.client.post('/beeswax/create/import_wizard/default', {
      'submit_create': 'on',
      'path': '/tmp/comma.dat.gz',
      'name': 'test_create_import',
      'delimiter_0': ',',
      'delimiter_1': '',
      'file_type': 'gzip',
      'do_import': 'True',
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
    assert_equal(resp.context['action'], 'watch-redirect')
    on_success_url_load_data = resp.context['on_success_url']
    assert_true('auto_load' in on_success_url_load_data, on_success_url_load_data)
    query_history = resp.context['query_history']

    resp = self.client.get(reverse('beeswax:api_fetch_query_history', kwargs={'query_history_id': query_history.id}), follow=True)
    content = json.loads(resp.content)
    watch_url = content['query_history']['watch_url']

    class MockResponse():
      def __init__(self, content):
        self.content = json.dumps(content)

    # Wait for CREATE TABLE to finis
    resp = wait_for_query_to_finish(self.client, MockResponse({'status': 'ok', 'watch_url': watch_url}), max=180.0)

    # Get URL that will load the data into the table. Also get the URL that will show the table in metastore app.
    resp = self.client.get(on_success_url_load_data, follow=True)
    assert_equal(resp.context['action'], 'watch-redirect')
    on_success_url_show_table = resp.context['on_success_url']
    assert_true('/metastore/table/' in on_success_url_show_table, on_success_url_show_table)
    query_history = resp.context['query_history']

    # Wait for load data to finish
    resp = wait_for_query_to_finish(self.client, MockResponse({'status': 'ok', 'watch_url': watch_url}), max=180.0)

    # Check data is in the table (by describing it)
    resp = self.client.get(on_success_url_show_table)
    cols = resp.context['table'].cols
    assert_equal(len(cols), 3)
    assert_equal([ col.name for col in cols ], [ 'col_a', 'col_b', 'col_c' ])
    assert_equal([['ta\tb', 'nada', 'sp ace'], ['f\too', 'bar', 'fred'], ['a\ta', 'bb', 'cc']], resp.context['sample'])
    assert_true("nada" in resp.content, resp.content)
    assert_true("sp&nbsp;ace" in resp.content, resp.content)

    # Test table creation and data loading and removing header
    resp = self.client.post('/beeswax/create/import_wizard/default', {
      'submit_create': 'on',
      'path': '/tmp/comma.csv',
      'name': 'test_create_import_with_header',
      'delimiter_0': ',',
      'delimiter_1': '',
      'file_type': 'text',
      'do_import': 'True',
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
    assert_equal(resp.context['action'], 'watch-redirect')
    on_success_url_load_data = resp.context['on_success_url']
    assert_true('auto_load' in on_success_url_load_data, on_success_url_load_data)
    query_history = resp.context['query_history']

    resp = self.client.get(reverse('beeswax:api_fetch_query_history', kwargs={'query_history_id': query_history.id}), follow=True)
    content = json.loads(resp.content)
    watch_url = content['query_history']['watch_url']

    # Wait for CREATE TABLE to finis
    resp = wait_for_query_to_finish(self.client, MockResponse({'status': 'ok', 'watch_url': watch_url}), max=180.0)

    # Get URL that will load the data into the table. Also get the URL that will show the table in metastore app.
    resp = self.client.get(on_success_url_load_data, follow=True)
    assert_equal(resp.context['action'], 'watch-redirect')
    on_success_url_show_table = resp.context['on_success_url']
    assert_true('/metastore/table/' in on_success_url_show_table, on_success_url_show_table)
    query_history = resp.context['query_history']

    # Wait for load data to finish
    resp = wait_for_query_to_finish(self.client, MockResponse({'status': 'ok', 'watch_url': watch_url}), max=180.0)

    # Check data is in the table (by describing it)
    resp = self.client.get(on_success_url_show_table)

    # Check data is in the table (by describing it)
    cols = resp.context['table'].cols
    assert_equal(len(cols), 3)
    assert_equal([ col.name for col in cols ], [ 'col_a', 'col_b', 'col_c' ])
    assert_equal(resp.context['sample'], [
      #['a', 'b', 'c'], # Gone as told to be header
      ['"a', 'a"', '"b'], # Hive does not support natively quoted CSV
      ['"a', '""a"', '"b']
    ] )


  def test_create_database(self):
    resp = self.client.post("/beeswax/create/database", {
      'name': 'my_db',
      'comment': 'foo',
      'create': 'Create database',
      'use_default_location': True,
    }, follow=True)
    resp = self.client.get(reverse("beeswax:api_watch_query_refresh_json", kwargs={'id': resp.context['query'].id}), follow=True)
    resp = wait_for_query_to_finish(self.client, resp, max=180.0)
    resp = self.client.get("/metastore/databases/")
    assert_true('my_db' in resp.context['databases'], resp)


  def test_select_query_server(self):
    c = make_logged_in_client()
    _make_query(c, 'SELECT bogus FROM test') # Improvement: mock another server

    history = beeswax.models.QueryHistory.objects.latest('id')
    assert_equal('beeswax', history.server_name)
    assert_equal(HIVE_SERVER_HOST.get(), history.server_host)
    assert_equal(HIVE_SERVER_TEST_PORT, history.server_port)

    query_server = history.get_query_server_config()
    assert_equal('beeswax', query_server['server_name'])
    assert_equal(get_localhost_name(), query_server['server_host'])
    assert_equal(HIVE_SERVER_TEST_PORT, query_server['server_port'])
    assert_equal('hiveserver2', query_server['server_type'])
    assert_true(query_server['principal'] is None, query_server['principal']) # No default hive/HOST_@TEST.COM so far


  def test_select_multi_db(self):
    response = _make_query(self.client, 'SELECT * FROM test LIMIT 5', local=False, database='default')
    response = wait_for_query_to_finish(self.client, response)
    content = fetch_query_result_data(self.client, response)
    assert_true([0, u'0x0'] in content['results'], content)

    response = _make_query(self.client, 'SHOW TABLES', local=False, database='other_db')
    response = wait_for_query_to_finish(self.client, response)
    content = fetch_query_result_data(self.client, response)
    assert_true('tab_name' in content['columns'][0]['name'], content)

    response = _make_query(self.client, 'SELECT * FROM test LIMIT 5', local=False, database='not_there')
    content = json.loads(response.content)
    assert_equal(-1, content.get('status'), content)


  def test_list_design_pagination(self):
    client = make_logged_in_client()

    _make_query(client, 'SELECT', name='my query history', submission_type='Save')
    design = SavedQuery.objects.get(name='my query history')

    for i in range(25):
      client.get('/beeswax/clone_design/%s' % (design.id,))

    resp = client.get('/beeswax/list_designs')
    ids_page_1 = set([query.id for query in resp.context['page'].object_list])
    resp = client.get('/beeswax/list_designs?q-page=2')
    ids_page_2 = set([query.id for query in resp.context['page'].object_list])
    for id in ids_page_2:
      assert_true(id not in ids_page_1)

    SavedQuery.objects.filter(name='my query history').delete()


  def test_get_table_sample(self):
    client = make_logged_in_client()

    resp = client.get(reverse('beeswax:describe_table', kwargs={'database': 'default', 'table': 'test'}) + '?sample=true')

    assert_equal(resp.status_code, 200)
    assert_true('<th>foo</th>' in resp.content, resp.content)
    assert_true([0, '0x0'] in resp.context['sample'], resp.context['sample'])


def test_import_gzip_reader():
  """Test the gzip reader in create table"""
  # Make gzipped data
  data = file(__file__).read()
  data_gz_sio = cStringIO.StringIO()
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
      assert_equal(len(resp.context['page'].object_list), 0)
    else:
      assert_true(len(resp.context['page'].object_list) >= n)     # Make the query run
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
  assert_equal({u'q-type': [u'beeswax']}, response.context['filter_params'])

  # Test pagination
  response = do_view('q-page=100', 0)
  assert_equal(0, len(response.context['page'].object_list))

  client = make_logged_in_client(username='test_who')
  grant_access('test_who', 'test_who', 'test_who')
  do_view('q-user=test_who', 0)
  do_view('q-user=:all')

def teststrip_trailing_semicolon():
  # Note that there are two queries (both an execute and an explain) scattered
  # in this file that use semicolons all the way through.

  # Single semicolon
  assert_equal("foo", strip_trailing_semicolon("foo;\n"))
  assert_equal("foo\n", strip_trailing_semicolon("foo\n;\n\n\n"))
  # Multiple semicolons: strip only last one
  assert_equal("fo;o;", strip_trailing_semicolon("fo;o;;     "))
  # No semicolons
  assert_equal("foo", strip_trailing_semicolon("foo"))

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
    beeswax.views._parse_out_hadoop_jobs(sample_log))
  assert_equal([], beeswax.views._parse_out_hadoop_jobs("nothing to see here"))

  sample_log_no_direct_url = """
14/06/09 08:40:38 INFO impl.YarnClientImpl: Submitted application application_1402269517321_0003
14/06/09 08:40:38 INFO mapreduce.Job: The url to track the job: N/A
14/06/09 08:40:38 INFO exec.Task: Starting Job = job_1402269517321_0003, Tracking URL = N/A
14/06/09 08:40:38 INFO exec.Task: Kill Command = /usr/lib/hadoop/bin/hadoop job  -kill job_1402269517321_0003
14/06/09 08:40:38 INFO cli.CLIService: OperationHandle [opType=EXECUTE_STATEMENT, getHandleIdentifier()=2168d15e-96d2-415a-8d49-e2535e82c2a4]: getOperationStatus()
"""
  assert_equal(
      ["job_1402269517321_0003"],
      beeswax.views._parse_out_hadoop_jobs(sample_log_no_direct_url))

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
  assert_true(search_log_line('ql.Driver', 'FAILED: Parse Error', logs))

  logs = "12/08/22 20:50:14 ERROR ql.Driver: FAILED: Parse Error: line 1:31 cannot recognize input near '''' '_this_is_not' 'SQL' in constant'"
  assert_true(search_log_line('ql.Driver', 'FAILED: Parse Error', logs))

  logs = """
    FAILED: Parse Error: line 1:31 cannot recognize input near '''' '_this_is_not' 'SQL' in constant
    2012-08-18 12:23:15,648 ERROR [pool-1-thread-2] ql.Driver (SessionState.java:printError(380)) - FAILED: Parse XXXX Error: line 1:31 cannot recognize input near '''' '_this_is_not' 'SQL' in constant
    org.apache.hadoop.hive.ql.parse.ParseException: line 1:31 cannot recognize input near '''' '_this_is_not' 'SQL' in constant
    """
  assert_false(search_log_line('ql.Driver', 'FAILED: Parse Error', logs))

  logs = """
    2012-08-18 12:23:15,648 ERROR [pool-1-thread-2] ql.Driver (SessionState.java:printError(380)) - FAILED: Parse
    Error: line 1:31 cannot recognize input near '''' '_this_is_not' 'SQL' in constant
    """
  assert_false(search_log_line('ql.Driver', 'FAILED: Parse Error', logs))


def test_split_statements():
  assert_equal([], hql_query(";;;").statements)
  assert_equal(["select * where id == '10'"], hql_query("select * where id == '10'").statements)
  assert_equal(["select * where id == '10'"], hql_query("select * where id == '10';").statements)
  assert_equal(['select', "select * where id == '10;' limit 100"], hql_query("select; select * where id == '10;' limit 100;").statements)
  assert_equal(['select', "select * where id == \"10;\" limit 100"], hql_query("select; select * where id == \"10;\" limit 100;").statements)
  assert_equal(['select', "select * where id == '\"10;\"\"\"' limit 100"], hql_query("select; select * where id == '\"10;\"\"\"' limit 100;").statements)

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
ROW FORMAT delimited fields terminated by ','  escaped by '\\'
STORED AS TEXTFILE
LOCATION '/user/admin/alltypes/alltypes';

USE functional;
ALTER TABLE alltypes ADD IF NOT EXISTS PARTITION(year=2009, month=1);
ALTER TABLE alltypes ADD IF NOT EXISTS PARTITION(year=2009, month=2);"""
  assert_equal(['CREATE DATABASE IF NOT EXISTS functional',
                'DROP TABLE IF EXISTS functional.alltypes',
                "CREATE EXTERNAL TABLE IF NOT EXISTS functional.alltypes (\nid int COMMENT 'Add a comment',\nbool_col boolean,\ntinyint_col tinyint,\nsmallint_col smallint,\nint_col int,\nbigint_col bigint,\nfloat_col float,\ndouble_col double,\ndate_string_col string,\nstring_col string,\ntimestamp_col timestamp)\nPARTITIONED BY (year int, month int)\nROW FORMAT delimited fields terminated by ','  escaped by '\\'\nSTORED AS TEXTFILE\nLOCATION '/user/admin/alltypes/alltypes'",
                'USE functional',
                'ALTER TABLE alltypes ADD IF NOT EXISTS PARTITION(year=2009, month=1)',
                'ALTER TABLE alltypes ADD IF NOT EXISTS PARTITION(year=2009, month=2)'
              ],
              hql_query(query).statements, hql_query(query).statements)


class MockHiveServerTable(HiveServerTable):

  def __init__(self, data):
    self.path_location = data.get('path_location')


class TestHiveServer2API():

  def test_partition_values(self):
    table = MockHiveServerTable({'path_location': '/my/table'})

    assert_equal(['2013022516'], PartitionValueCompatible(['datehour=2013022516'], table).values)
    assert_equal(['2011-07', '2011-07-01', '12'], PartitionValueCompatible(['month=2011-07/dt=2011-07-01/hr=12'], table).values)

  def test_table_properties(self):
    table = MockHiveServerTable({})
    prev_extended_describe = getattr(MockHiveServerTable, 'extended_describe')

    try:
      extended_describe = 'Table(tableName:page_view, dbName:default, owner:romain, createTime:1360732885, lastAccessTime:0, retention:0, sd:StorageDescriptor(cols:[FieldSchema(name:viewtime, type:int, comment:null), FieldSchema(name:userid, type:bigint, comment:null), FieldSchema(name:page_url, type:string, comment:null), FieldSchema(name:referrer_url, type:string, comment:null), FieldSchema(name:ip, type:string, comment:IP Address of the User), FieldSchema(name:dt, type:string, comment:null), FieldSchema(name:country, type:string, comment:null)], location:hdfs://localhost:8020/user/hive/warehouse/page_view, inputFormat:org.apache.hadoop.mapred.TextInputFormat, outputFormat:org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat, compressed:false, numBuckets:-1, serdeInfo:SerDeInfo(name:null, serializationLib:org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe, parameters:{serialization.format=1}), bucketCols:[], sortCols:[], parameters:{}, skewedInfo:SkewedInfo(skewedColNames:[], skewedColValues:[], skewedColValueLocationMaps:{}), storedAsSubDirectories:false), partitionKeys:[FieldSchema(name:dt, type:string, comment:null), FieldSchema(name:country, type:string, comment:null)], parameters:{numPartitions=0, numFiles=1, transient_lastDdlTime=1360732885, comment=This is the page view table}, viewOriginalText:null, viewExpandedText:null, tableType:MANAGED_TABLE)'
      setattr(table, 'extended_describe', extended_describe)

      assert_equal([['tableName', 'page_view'],
                    ['dbName', 'default'],
                    ['owner', 'romain'],
                    ['createTime', '1360732885'],
                    ['lastAccessTime', '0'],
                    ['retention', '0'],
                    ['location:hdfs://localhost', '8020/user/hive/warehouse/page_view'],
                    ['inputFormat', 'org.apache.hadoop.mapred.TextInputFormat'],
                    ['outputFormat', 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'],
                    ['compressed', 'false'],
                    ['numBuckets', '-1'],
                    ['serdeInfo:SerDeInfo(name', 'null'],
                    ['serializationLib', 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'],
                    ['parameters', '{serialization.format=1})'],
                    ['bucketCols', '[]'],
                    ['sortCols', '[]'],
                    ['parameters', '{}'],
                    ['skewedInfo:SkewedInfo(skewedColNames', '[]'],
                    ['skewedColValues', '[]'],
                    ['skewedColValueLocationMaps', '{})'],
                    ['storedAsSubDirectories', 'false)'],
                    ['partitionKeys:[FieldSchema(name', 'dt'],
                    ['type', 'string'],
                    ['comment', 'null)'],
                    ['FieldSchema(name', 'country'],
                    ['type', 'string'],
                    ['comment', 'null)]'],
                    ['parameters', '{numPartitions=0'],
                    ['numFiles', '1'],
                    ['transient_lastDdlTime', '1360732885'],
                    ['comment', 'This is the page view table}'],
                    ['viewOriginalText', 'null'],
                    ['viewExpandedText', 'null'],
                    ['tableType', 'MANAGED_TABLE']
                  ],
                  table.properties)
    finally:
      setattr(table, 'extended_describe', prev_extended_describe)


class MockDbms:

  def __init__(self, client, server_type):
    pass

  def get_databases(self):
    return ['default', 'test']

  def get_tables(self, database):
    return ['table1', 'table2']


class TestWithMockedServer(object):

  def setUp(self):
    # Beware: Monkey patch Beeswax/Hive server with Mock API
    if not hasattr(dbms, 'OriginalBeeswaxApi'):
      dbms.OriginalBeeswaxApi = dbms.HiveServer2Dbms
    dbms.HiveServer2Dbms = MockDbms

    self.client = make_logged_in_client(is_superuser=False)
    self.client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test')
    self.user = User.objects.get(username='test')
    self.user_not_me = User.objects.get(username='not_me')
    grant_access("test", "test", "beeswax")

  def tearDown(self):
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
    ids_page_1 = set([query.id for query in resp.context['page'].object_list])
    assert_equal(2, sum([query_id in ids_page_1 for query_id in ids]))

    resp = self.client.post(reverse('beeswax:delete_design'), {u'skipTrash': [u'false'], u'designs_selection': ids})
    queries = SavedQuery.objects.filter(id__in=ids)
    assert_true(queries[0].doc.get().is_trashed())
    assert_true(queries[1].doc.get().is_trashed())

    resp = self.client.get('/beeswax/list_designs')
    ids_page_1 = set([query.id for query in resp.context['page'].object_list])
    assert_equal(0, sum([query_id in ids_page_1 for query_id in ids]))

    resp = self.client.post(reverse('beeswax:restore_design'), {u'skipTrash': [u'false'], u'designs_selection': ids})
    query = SavedQuery.objects.filter(id__in=ids)
    assert_false(queries[0].doc.get().is_trashed())
    assert_false(queries[1].doc.get().is_trashed())

    resp = self.client.get('/beeswax/list_designs')
    ids_page_1 = set([query.id for query in resp.context['page'].object_list])
    assert_equal(2, sum([query_id in ids_page_1 for query_id in ids]))

    resp = self.client.post(reverse('beeswax:delete_design'), {u'skipTrash': [u'false'], u'designs_selection': ids})
    query = SavedQuery.objects.filter(id__in=ids)
    assert_true(queries[0].doc.get().is_trashed())
    assert_true(queries[1].doc.get().is_trashed())

    resp = self.client.get('/beeswax/list_designs')
    ids_page_1 = set([query.id for query in resp.context['page'].object_list])
    assert_equal(0, sum([query_id in ids_page_1 for query_id in ids]))

    resp = self.client.post(reverse('beeswax:delete_design'), {u'skipTrash': [u'true'], u'designs_selection': ids})
    assert_false(SavedQuery.objects.filter(id__in=ids).exists())

    resp = self.client.get('/beeswax/list_designs')
    ids_page_1 = set([query.id for query in resp.context['page'].object_list])
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


class TestDesign():

  def test_hql_resource(self):
    design = hql_query('SELECT')
    design._data_dict['file_resources'] = [
        {'type': 'FILE', 'path': 'my_file'},
        {'type': 'FILE', 'path': '/my_path/my_file'},
        {'type': 'FILE', 'path': 's3://host/my_s3_file'}
    ]

    statements = design.get_configuration_statements()
    assert_true(re.match('\nADD FILE hdfs://([^:]+):(\d+)my_file\n', statements[0]), statements[0])
    assert_true(re.match('\nADD FILE hdfs://([^:]+):(\d+)/my_path/my_file\n', statements[1]), statements[1])
    assert_equal('\nADD FILE s3://host/my_s3_file\n', statements[2])


def search_log_line(component, expected_log, all_logs):
  """Checks if 'expected_log' can be found in one line of 'all_logs' outputed by the logging component 'component'."""
  return re.compile('.+?%(component)s(.+?)%(expected_log)s' % {'component': component, 'expected_log': expected_log}).search(all_logs)


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
    beeswax_query_server = {'server_name': 'beeswax', 'principal': 'hive'}
    beeswax_query_server.update(default_query_server)
    assert_equal((True, 'PLAIN', 'hive', False, None, None), HiveServerClient(beeswax_query_server, user).get_security())

    # HiveServer2 LDAP passthrough
    finish = []
    finish.append(LDAP_USERNAME.set_for_testing('hueabcd'))
    finish.append(LDAP_PASSWORD.set_for_testing('abcd'))
    try:
      assert_equal((True, 'PLAIN', 'hive', False, 'hueabcd', 'abcd'), HiveServerClient(beeswax_query_server, user).get_security())
    finally:
      for f in finish:
        f()

    hive_site._HIVE_SITE_DICT[hive_site._CNF_HIVESERVER2_AUTHENTICATION] = 'NOSASL'
    hive_site._HIVE_SITE_DICT[hive_site._CNF_HIVESERVER2_IMPERSONATION] = 'true'
    assert_equal((False, 'NOSASL', 'hive', True, None, None), HiveServerClient(beeswax_query_server, user).get_security())
    hive_site._HIVE_SITE_DICT[hive_site._CNF_HIVESERVER2_AUTHENTICATION] = 'KERBEROS'
    assert_equal((True, 'GSSAPI', 'hive', True, None, None), HiveServerClient(beeswax_query_server, user).get_security())

    # Impala
    impala_query_server = {'server_name': 'impala', 'principal': 'impala', 'impersonation_enabled': False}
    impala_query_server.update(default_query_server)
    assert_equal((False, 'GSSAPI', 'impala', False, None, None), HiveServerClient(impala_query_server, user).get_security())

    impala_query_server = {'server_name': 'impala', 'principal': 'impala', 'impersonation_enabled': True}
    impala_query_server.update(default_query_server)
    assert_equal((False, 'GSSAPI', 'impala', True, None, None), HiveServerClient(impala_query_server, user).get_security())

    cluster_conf = hadoop.cluster.get_cluster_conf_for_job_submission()
    finish = cluster_conf.SECURITY_ENABLED.set_for_testing(True)
    try:
      assert_equal((True, 'GSSAPI', 'impala', True, None, None), HiveServerClient(impala_query_server, user).get_security())
    finally:
      finish()
  finally:
    if prev is not None:
      hive_site._HIVE_SITE_DICT[hive_site._CNF_HIVESERVER2_AUTHENTICATION] = prev
    else:
      hive_site._HIVE_SITE_DICT.pop(hive_site._CNF_HIVESERVER2_AUTHENTICATION, None)


class MockClient():

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
