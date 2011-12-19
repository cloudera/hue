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
#
# Tests for beeswax

import cStringIO
import gzip
import logging
import os
import re
import shutil
import tempfile
import threading
from nose.tools import assert_true, assert_equal, assert_false
from nose.plugins.skip import SkipTest
from django.utils.encoding import smart_str

from desktop.lib.django_test_util import make_logged_in_client, assert_equal_mod_whitespace
from desktop.lib.django_test_util import assert_similar_pages
from desktop.lib.test_export_csvxls import xls2csv

import beeswax.create_table
import beeswax.db_utils
import beeswax.forms
import beeswax.hive_site
import beeswax.models
import beeswax.report
import beeswax.views
from beeswax.views import parse_results, collapse_whitespace
from beeswax.test_base import make_query, wait_for_query_to_finish, verify_history
from beeswax.test_base import BeeswaxSampleProvider
from beeswaxd import BeeswaxService

LOG = logging.getLogger(__name__)
CSV_LINK_PAT = re.compile('/beeswax/download/\d+/csv')

def _make_query(client, query, submission_type="Execute",
                udfs=None, settings=None, resources=[],
                wait=False, name=None, desc=None, local=True,
                is_parameterized=True, max=30.0, **kwargs):
  """Wrapper around the real make_query"""
  res = make_query(client, query, submission_type,
                   udfs, settings, resources,
                   wait, name, desc, local, is_parameterized, max, **kwargs)
  # Should be in the history if it's submitted.
  if submission_type == 'Execute':
    fragment = collapse_whitespace(smart_str(query[:20]))
    verify_history(client, fragment=fragment)

  return res


def get_csv(client, result_response):
  """Get the csv for a query result"""
  csv_link = CSV_LINK_PAT.search(result_response.content)
  assert_true(csv_link, "Query result should have a csv download link")
  return client.get(csv_link.group()).content


class TestBeeswaxWithHadoop(BeeswaxSampleProvider):
  """Tests for beeswax that require a running Hadoop"""
  requires_hadoop = True

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
    """
    Creating a table "again" should not work; error should be displayed.
    """
    response = _make_query(self.client, "CREATE TABLE test (foo INT)", wait=True)
    assert_true("Table test already exists" in response.content)
    assert_true("Table test already exists" in response.context["error_message"])

  def test_configuration(self):
    response = self.client.get("/beeswax/configuration")
    response_verbose = self.client.get("/beeswax/configuration?include_hadoop=true")

    assert_true("Scratch space for Hive jobs" in response.content)
    assert_true("hive.exec.scratchdir" in response.content)

    assert_true("tasktracker.http.threads" in response_verbose.content)
    assert_true("tasktracker.http.threads" not in response.content)

  def test_describe_partitions(self):
    response = self.client.get("/beeswax/table/test_partitions/partitions")
    assert_true("baz_one" in response.content)
    assert_true("boom_two" in response.content)
    response = self.client.get("/beeswax/table/test/partitions")
    assert_true("is not partitioned." in response.content)

  def test_browse_partitions_with_limit(self):
    # Limit to 90
    finish = beeswax.conf.BROWSE_PARTITIONED_TABLE_LIMIT.set_for_testing("90")
    try:
      response = self.client.get("/beeswax/table/test_partitions")
      assert_true("89" in response.content)
      assert_false("90" in response.content)
    finally:
      finish()

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
    assert_equal([['0'], ['1'], ['4'], ['9']], response.context["results"][0:4])

  def test_query_with_setting(self):
    response = _make_query(self.client, "CREATE TABLE test2 AS SELECT foo+1 FROM test WHERE foo=4",
      settings=[("mapred.job.name", "test_query_with_setting"),
        ("hive.exec.compress.output", "true")], local=False) # Run on MR, because that's how we check it worked.
    response = wait_for_query_to_finish(self.client, response, max=180.0)
    # Check that we actually got a compressed output
    files = self.cluster.fs.listdir("/user/hive/warehouse/test2")
    assert_true(len(files) >= 1)
    assert_true(files[0].endswith(".deflate"))
    # And check that the name is right...
    assert_true("test_query_with_setting" in [ x.profile.name for x in self.cluster.jt.all_jobs().jobs ])

    # While we're at it, check that we're running jobs as the correct user on MR.
    assert_equal("test",
      [ x.profile for x in self.cluster.jt.all_jobs().jobs
        if x.profile.name == "test_query_with_setting" ][0].user)

  def test_basic_flow(self):
    """
    Test basic query submission
    """
    # Minimal server operation
    assert_equal("echo", beeswax.db_utils.db_client().echo("echo"))

    # Table should have been created
    response = self.client.get("/beeswax/tables")
    assert_true("test" in response.context["tables"])

    # And have detail
    response = self.client.get("/beeswax/table/test")
    assert_true("foo" in response.content)

    # Remember the number of history items. Use a generic fragment 'test' to pass verification.
    history_cnt = verify_history(self.client, fragment='test')

    # Show table data.
    response = self.client.get("/beeswax/table/test/read", follow=True)
    response = wait_for_query_to_finish(self.client, response, max=30.0)
    # Note that it may not return all rows at once. But we expect at least 10.
    assert_true(len(response.context['results']) > 10)
    # This should NOT go into the query history.
    assert_equal(verify_history(self.client, fragment='test'), history_cnt,
                 'Implicit queries should not be saved in the history')
    assert_equal(str(response.context['query_context'][0]), 'table')
    assert_equal(str(response.context['query_context'][1]), 'test')

    # Query the data
    # We use a semicolon here for kicks; the code strips it out.
    QUERY = """
      SELECT MIN(foo), MAX(foo), SUM(foo) FROM test;
    """
    response = _make_query(self.client, QUERY)
    assert_true(response.redirect_chain[0][0].startswith("http://testserver/beeswax/watch/"))
    # Check that we report this query as "running". (This query takes a while.)
    self._verify_query_state(beeswax.models.QueryHistory.STATE.running)

    response = wait_for_query_to_finish(self.client, response, max=180.0)
    assert_equal(["0", "255", "32640"], response.context["results"][0])
    # Because it happens that we're running this with mapred.job.tracker,
    # we won't see any hadoop jobs.
    assert_equal(0, len(response.context["hadoop_jobs"]), "Shouldn't have found jobs.")
    self._verify_query_state(beeswax.models.QueryHistory.STATE.available)

    # Query multi-page request
    QUERY = """
      SELECT * FROM test
    """
    response = _make_query(self.client, QUERY, name='select star', local=False)
    assert_equal(2, len(response.context["download_urls"]))
    response = wait_for_query_to_finish(self.client, response)
    assert_equal(str(response.context['query_context'][0]), 'design')
    assert_true("<td>99</td>" in response.content)
    assert_true(response.context["has_more"])
    response = self.client.get("/beeswax/results/%d/%d" % (response.context["query"].id, response.context["next_row"]))
    assert_true("<td>199</td>" in response.content)
    response = self.client.get("/beeswax/results/%d/0" % (response.context["query"].id))
    assert_true("<td>99</td>" in response.content)
    assert_equal(0, len(response.context["hadoop_jobs"]), "SELECT * shouldn't have started jobs.")

    # Download the data
    response = self.client.get(response.context["download_urls"]["csv"])
    # Header line plus data lines...
    assert_equal(257, response.content.count("\n"))

  def test_query_with_udf(self):
    """
    Testing query with udf
    """
    response = _make_query(self.client, "SELECT my_sqrt(foo), my_power(foo, foo) FROM test WHERE foo=4",
      udfs=[('my_sqrt', 'org.apache.hadoop.hive.ql.udf.UDFSqrt'),
        ('my_power', 'org.apache.hadoop.hive.ql.udf.UDFPower')], local=False)
    response = wait_for_query_to_finish(self.client, response, max=60.0)
    assert_equal(["2.0", "256.0"], response.context["results"][0])
    log = response.context['log']
    assert_true('ql.Driver: Total MapReduce jobs' in log, 'Captured log from Driver')
    assert_true('exec.MapRedTask: Starting Job = job_' in log, 'Captured log from MapRedTask')
    # Test job extraction while we're at it
    assert_equal(1, len(response.context["hadoop_jobs"]), "Should have started 1 job and extracted it.")

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
    """Test handling syntax error"""
    def check_error_in_response(response):
      assert_true("Parse Error" in response.context["error_message"])
      log = response.context['log']
      assert_true(len(log.split('\n')) > 10, 'Captured stack trace')
      assert_true('org.apache.hadoop.hive.ql.parse.ParseException: line' in log,
                  'Captured stack trace')

    hql = "SELECT KITTENS ARE TASTY"
    resp = _make_query(self.client, hql, name='tasty kittens')
    check_error_in_response(resp)
    id = self._verify_query_state(beeswax.models.QueryHistory.STATE.failed)

    # Test that we can view the error again
    resp = self.client.get('/beeswax/watch/%s' % (id,), follow=True)
    check_error_in_response(resp)

  def test_parameterization(self):
    """
    Test parameterization
    """
    response = _make_query(self.client, "SELECT foo FROM test WHERE foo='$x' and bar='$y'", is_parameterized=False)
    # Assert no parameterization was offered
    assert_equal("watch_wait.mako", response.template, "we should have seen the template for a query executing")

    response = _make_query(self.client, "SELECT foo FROM test WHERE foo='$x' and bar='$y'")
    assert_true("parameterization.mako", response.template)
    assert_true(["x", "y"], response.context["form"].fields.keys())
    design_id = response.context["design"].id

    # Don't fill out the form
    response = self.client.post("/beeswax/execute_parameterized/%d" % design_id)
    assert_true("parameterization.mako", response.template)

    # Now fill it out
    response = self.client.post("/beeswax/execute_parameterized/%d" % design_id,
      { "parameterization-x": str(1), "parameterization-y": str(2) }, follow=True)

    assert_equal("watch_wait.mako", response.template)
    # Check that substitution happened!
    assert_equal("SELECT foo FROM test WHERE foo='1' and bar='2'",
      response.context["query"].query)

    # Check that error handling is reasonable
    response = self.client.post("/beeswax/execute_parameterized/%d" % design_id,
      { "parameterization-x": "'_this_is_not SQL ", "parameterization-y": str(2) }, follow=True)
    assert_true("execute.mako" in response.template)
    assert_true("ql.Driver: FAILED: Parse Error" in response.context["log"])

  def test_explain_query(self):
    c = self.client
    response = _make_query(c, "SELECT KITTENS ARE TASTY", submission_type="Explain")
    assert_true("Parse Error" in response.context["error_message"])
    CREATE_TABLE = "CREATE TABLE test_explain (foo INT, bar STRING);"
    response = _make_query(c, CREATE_TABLE)
    wait_for_query_to_finish(c, response)

    response = _make_query(c, "SELECT SUM(foo) FROM test_explain", submission_type="Explain")
    assert_true(response.context["explanation"])

  def test_explain_query_i18n(self):
    query = u"SELECT foo FROM test_utf8 WHERE bar='%s'" % (unichr(200),)
    response = _make_query(self.client, query, submission_type="Explain")
    assert_true(response.context['explanation'])

  def test_query_i18n(self):
    # Test fails because HIVE_PLAN cannot be found and raises FileNotFoundException
    # because of a Hive bug.
    raise SkipTest

    # Selecting from utf-8 table should get correct result
    query = u"SELECT * FROM test_utf8 WHERE bar='%s'" % (unichr(200),)
    response = _make_query(self.client, query, wait=True)
    assert_equal(["200", unichr(200)], response.context["results"][0],
                 "selecting from utf-8 table should get correct result")

    csv = get_csv(self.client, response)
    assert_equal('"200","%s"' % (unichr(200).encode('utf-8'),), csv.split()[1])

    # Selecting from latin1 table should not blow up
    query = u"SELECT * FROM test_latin1 WHERE bar='%s'" % (unichr(200),)
    response = _make_query(self.client, query, wait=True)
    assert_true(response.context.has_key("results"),
                "selecting from latin1 table should not blow up")

    # Describe table should be fine with non-ascii comment
    response = self.client.get('/beeswax/table/test_utf8')
    assert_equal(response.context['table'].parameters['comment'],
                 self.get_i18n_table_comment())

  def _parallel_query_helper(self, i, result_holder, lock, num_tasks):
    client = make_logged_in_client()
    try:
      q = "SELECT foo+" + str(i + 1) + " FROM test WHERE foo < 2"
      LOG.info("Starting " + str(i) + ": " + q)
      response = _make_query(client, q)
      response = wait_for_query_to_finish(client, response, max=(240.0*num_tasks))
      lock.acquire()
      result_holder[i] = response
      lock.release()
      LOG.info("Finished: " + str(i))
    except:
      LOG.exception("Saw exception in child thread.")

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
    query_msg = BeeswaxService.Query()
    query_msg.query = 'SELECT foo FROM test limit %d' % (limit,)
    query_msg.configuration = []
    query_msg.hadoop_user = "test"
    handle = beeswax.db_utils.db_client().query(query_msg)
    query_data = beeswax.models.QueryHistory(server_id=handle.id, log_context=handle.log_context)
    # Get the result in csv. Should have 3 + 1 header row.
    csv_resp = beeswax.data_export.download(query_data, 'csv')
    assert_equal(len(csv_resp.content.strip().split('\n')), limit + 1)

  def test_data_export(self):
    query_msg = BeeswaxService.Query()
    query_msg.query = 'SELECT * FROM test'
    query_msg.configuration = []
    query_msg.hadoop_user = "test"
    handle = beeswax.db_utils.db_client().query(query_msg)
    query_data = beeswax.models.QueryHistory(server_id=handle.id, log_context=handle.log_context)
    # Get the result in xls. Then translate it into csv.
    xls_resp = beeswax.data_export.download(query_data, 'xls')
    translated_csv = xls2csv(xls_resp.content)
    # It should have 257 lines (256 + header)
    assert_equal(len(translated_csv.strip('\r\n').split('\r\n')), 257)
    handle = beeswax.db_utils.db_client().query(query_msg)
    # Get the result in csv.
    csv_resp = beeswax.data_export.download(query_data, 'csv')
    assert_equal(csv_resp.content, translated_csv)

  def test_designs(self):
    """Test design view and interaction"""
    cli = self.client

    # An auto hql design should be created, and it should ignore the given name and desc
    _make_query(self.client, 'SELECT bogus FROM test', name='mydesign', desc='hyatt')
    resp = cli.get('/beeswax/list_designs')
    n_designs = len(resp.context['page'].object_list)

    # Retrieve that design. It's the first one since it's most recent
    design = beeswax.models.SavedQuery.objects.all()[0]
    resp = cli.get('/beeswax/execute/%s' % (design.id,))
    assert_true('SELECT bogus FROM test' in resp.content)

    # Make a valid auto hql design
    resp = _make_query(self.client, 'SELECT * FROM test')
    wait_for_query_to_finish(self.client, resp, max=60.0)

    resp = cli.get('/beeswax/list_designs')
    nplus_designs = len(resp.context['page'].object_list)
    assert_true(nplus_designs == n_designs,
                'Auto design should not show up in list_designs')

    # Test explicit save
    query = 'MORE BOGUS JUNKS FROM test'
    exe_resp = _make_query(self.client, query, name='rubbish', submission_type='Save')
    assert_true(exe_resp.context.get("error_message") is None)
    resp = cli.get('/beeswax/list_designs')
    assert_true('rubbish' in resp.content)
    nplusplus_designs = len(resp.context['page'].object_list)
    assert_true(nplusplus_designs > nplus_designs)

    # Retrieve that design
    design = beeswax.models.SavedQuery.objects.filter(name='rubbish')[0]
    resp = cli.get('/beeswax/execute/%s' % (design.id,))
    assert_similar_pages(resp.content, exe_resp.content)

    # Clone the rubbish design
    len_before = len(beeswax.models.SavedQuery.objects.filter(name__contains='rubbish'))
    resp = cli.get('/beeswax/clone_design/%s' % (design.id,))
    len_after = len(beeswax.models.SavedQuery.objects.filter(name__contains='rubbish'))
    assert_true(len_after == len_before + 1)

    # Delete a design
    resp = cli.get('/beeswax/delete_design/1')
    assert_true('sure?' in resp.content)
    resp = cli.post('/beeswax/delete_design/1')
    assert_true(resp.template == 'list_designs.mako')

    # Helper to test the view, filtering, etc
    def do_view(param):
      resp = cli.get('/beeswax/list_designs?' + param)
      assert_true(len(resp.context['page'].object_list) >= 0)     # Make the query run
      return resp

    do_view('user=test')
    do_view('text=whatever')
    do_view('type=hql')
    do_view('type=report')
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


  def test_my_queries(self):
    """Test the "My Queries" page"""
    # Explicit save a design
    _make_query(self.client, "select noHQL", name='my rubbish kuery', submission_type='Save')
    # Run something
    _make_query(self.client, "Even More Bogus Junk")
    resp = self.client.get('/beeswax/my_queries')
    assert_true('my rubbish kuery' in resp.content)
    assert_true('Even More Bogus Junk' in resp.content)

    # Login as someone else
    client2 = make_logged_in_client('not_me')
    resp = client2.get('/beeswax/my_queries')
    assert_true('my rubbish kuery' not in resp.content)
    assert_true('Even More Bogus Junk' not in resp.content)
    client2.logout()


  def test_load_data(self):
    """
    Test load data queries.
    These require Hadoop, because they ask the metastore
    about whether a table is partitioned.
    """
    # Check that view works
    resp = self.client.get("/beeswax/table/test/load")
    assert_true(resp.context["form"])

    # Try the submission
    resp = self.client.post("/beeswax/table/test/load", dict(path="/tmp/foo", overwrite=True))
    assert_equal_mod_whitespace("LOAD DATA INPATH '/tmp/foo' OVERWRITE INTO TABLE `test`",
        resp.context["form"].query.initial["query"])
    resp = self.client.post("/beeswax/table/test/load", dict(path="/tmp/foo", overwrite=False))
    assert_equal_mod_whitespace("LOAD DATA INPATH '/tmp/foo' INTO TABLE `test`",
        resp.context["form"].query.initial["query"])

    # Try it with partitions
    resp = self.client.post("/beeswax/table/test_partitions/load", dict(path="/tmp/foo", partition_0="alpha", partition_1="beta"))
    assert_equal_mod_whitespace("LOAD DATA INPATH '/tmp/foo' INTO TABLE `test_partitions` PARTITION (baz='alpha', boom='beta')",
        resp.context["form"].query.initial["query"])


  def test_save_results_to_dir(self):
    """Check that saving to directory works"""

    def save_and_verify(select_resp, target_dir, verify=True):
      qid = select_resp.context['query'].id
      save_data = {
        'save_target': beeswax.forms.SaveResultsForm.SAVE_TYPE_DIR,
        'target_dir': target_dir,
        'save': True
      }
      resp = self.client.post('/beeswax/save_results/%s' % (qid,), save_data, follow=True)
      wait_for_query_to_finish(self.client, resp, max=60)

      # Check that data is right
      if verify:
        target_ls = self.cluster.fs.listdir(target_dir)
        assert_true(len(target_ls) >= 1)
        data_buf = ""
        for target in target_ls:
          target_file = self.cluster.fs.open(target_dir + '/' + target)
          data_buf += target_file.read()
          target_file.close()

        assert_equal(256, len(data_buf.strip().split('\n')))
        assert_true('255' in data_buf)
      return resp

    TARGET_DIR_ROOT = '/tmp/beeswax.test_save_results'

    # Not supported. SELECT *. (Result dir is same as table dir.)
    hql = "SELECT * FROM test"
    resp = _make_query(self.client, hql, wait=True, local=False, max=180.0)
    resp = save_and_verify(resp, TARGET_DIR_ROOT + '/1', verify=False)
    assert_true('not supported' in resp.content)

    # SELECT columns. (Result dir is in /tmp.)
    hql = "SELECT foo, bar FROM test"
    resp = _make_query(self.client, hql, wait=True, local=False, max=180.0)
    resp = save_and_verify(resp, TARGET_DIR_ROOT + '/2')
    # Results has a link to the FB
    assert_true('Query results stored in' in resp.content)
    assert_true('filebrowser' in resp.content)

    # Not supported. Partition tables
    hql = "SELECT * FROM test_partitions"
    resp = _make_query(self.client, hql, wait=True, local=False, max=180.0)
    resp = save_and_verify(resp, TARGET_DIR_ROOT + '/3', verify=False)
    assert_true('not supported' in resp.content)


  def test_save_results_to_tbl(self):
    """Check that saving to new table works"""

    def save_and_verify(select_resp, target_tbl):
      """Check that saving to table works"""
      qid = select_resp.context['query'].id
      save_data = {
        'save_target': beeswax.forms.SaveResultsForm.SAVE_TYPE_TBL,
        'target_table': target_tbl,
        'save': True
      }
      resp = self.client.post('/beeswax/save_results/%s' % (qid,), save_data, follow=True)
      wait_for_query_to_finish(self.client, resp, max=120)

      # Check that data is right. The SELECT may not give us the whole table.
      resp = _make_query(self.client, 'SELECT * FROM %s' % (target_tbl,), wait=True,
                        local=False)
      for i in xrange(90):
        assert_equal([str(i), '0x%x' % (i,)], resp.context['results'][i])

    TARGET_TBL_ROOT = 'test_copy'

    # SELECT *. (Result dir is same as table dir.)
    hql = "SELECT * FROM test"
    resp = _make_query(self.client, hql, wait=True, local=False, max=180.0)
    save_and_verify(resp, TARGET_TBL_ROOT + '_1')

    # SELECT columns. (Result dir is in /tmp.)
    hql = "SELECT foo, bar FROM test"
    resp = _make_query(self.client, hql, wait=True, local=False, max=180.0)
    save_and_verify(resp, TARGET_TBL_ROOT + '_2')


  def test_install_examples(self):
    """
    Test installation of examples
    """
    assert_true(not beeswax.models.MetaInstall.get().installed_example)
    self.client.post('/beeswax/install_examples')

    # New tables exists
    resp = self.client.get('/beeswax/tables')
    assert_true('sample_08' in resp.content)
    assert_true('sample_07' in resp.content)

    # New designs exists
    resp = self.client.get('/beeswax/list_designs')
    assert_true('Sample: Job loss' in resp.content)
    assert_true('Sample: Salary growth' in resp.content)
    assert_true('Sample: Top salary' in resp.content)
    assert_true(beeswax.models.MetaInstall.get().installed_example)

    # Now install it a second time, and expect an error
    resp = self.client.post('/beeswax/install_examples')
    assert_true("error" in resp.content)
    assert_true("already installed" in resp.content)

    # First, unset the db entry to allow installation to re-run
    meta = beeswax.models.MetaInstall.get()
    meta.installed_example = False
    meta.save()

    # Now it should complain
    resp = self.client.post('/beeswax/install_examples')
    assert_true("error" in resp.content)
    assert_true("already exists" in resp.content)


  def test_create_table_generation(self):
    """
    Checks HQL generation for create table.

    NOT TESTED/DONE: Validation checks for the inputs.
    """
    # Make sure we get a form
    resp = self.client.get("/beeswax/create/create_table")
    assert_true("Field terminator" in resp.content)
    # Make a submission
    resp = self.client.post("/beeswax/create/create_table", {
      'table-name': 'my_table',
      'table-comment': 'Yo>>>>dude',  # Make sure escaping is sort of ok.
      'table-row_format': 'Delimited',
      'table-field_terminator_0': r'\001',
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
    })

    assert_equal_mod_whitespace(r"""
        CREATE EXTERNAL TABLE `my_table`
        (
         `my_col` string
        )
        COMMENT "Yo>>>>dude"
        ROW FORMAT DELIMITED
          FIELDS TERMINATED BY '\001'
          COLLECTION ITEMS TERMINATED BY '\002'
          MAP KEYS TERMINATED BY '\003'
          STORED AS TextFile LOCATION "/tmp/foo"
    """, resp.context["form"].query.initial["query"])

    assert_true('/beeswax/table/my_table' in resp.context['on_success_url'])


  def test_partitioned_create_table(self):
    """
    Test HQL generation of create table with partition columns
    """
    # Make sure we get a form
    resp = self.client.get("/beeswax/create/create_table")
    assert_true("Field terminator" in resp.content)
    # Make a submission
    resp = self.client.post("/beeswax/create/create_table", {
      'table-name': 'my_table',
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
    })

    assert_equal_mod_whitespace(r"""
        CREATE TABLE `my_table`
        (
         `my_col` string
        )
        PARTITIONED BY
        (
          `my_partition` string
        )
        ROW FORMAT DELIMITED
          FIELDS TERMINATED BY '\001'
          COLLECTION ITEMS TERMINATED BY '\002'
          MAP KEYS TERMINATED BY '\003'
          STORED AS TextFile
    """, resp.context["form"].query.initial["query"])


  def test_create_table_dependencies(self):
    """
    Test field dependency in the create table form
    """
    resp = self.client.post("/beeswax/create/create_table", {
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
      ['a\ta', 'bb', 'cc'] ]

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

    write_file('/tmp/spacé.dat', RAW_FIELDS, ' ')
    write_file('/tmp/tab.dat', RAW_FIELDS, '\t')
    write_file('/tmp/comma.dat', RAW_FIELDS, ',')
    write_file('/tmp/comma.dat.gz', RAW_FIELDS, ',', do_gzip=True)

    # Test auto delim selection
    resp = self.client.post('/beeswax/create/import_wizard', {
      'submit_file': 'on',
      'path': '/tmp/comma.dat',
      'name': 'test_create_import',
    })
    assert_equal(resp.context['fields_list'], RAW_FIELDS)

    # Test same with gzip
    resp = self.client.post('/beeswax/create/import_wizard', {
      'submit_file': 'on',
      'path': '/tmp/comma.dat.gz',
      'name': 'test_create_import',
    })
    assert_equal(resp.context['fields_list'], RAW_FIELDS)

    # Make sure space works
    resp = self.client.post('/beeswax/create/import_wizard', {
      'submit_preview': 'on',
      'path': '/tmp/spacé.dat',
      'name': 'test_create_import',
      'delimiter_0': ' ',
      'delimiter_1': '',
      'file_type': 'text',
    })
    assert_equal(len(resp.context['fields_list'][0]), 4)

    # Test column definition
    resp = self.client.post('/beeswax/create/import_wizard', {
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
    resp = self.client.post('/beeswax/create/import_wizard', {
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

    resp = wait_for_query_to_finish(self.client, resp, max=180.0)

    # Check data is in the table (by describing it)
    resp = self.client.get('/beeswax/table/test_create_import')
    sd = resp.context['table'].sd
    assert_equal(len(sd.cols), 3)
    assert_equal([ col.name for col in sd.cols ], [ 'col_a', 'col_b', 'col_c' ])
    assert_true("<td>nada</td>" in resp.content)
    assert_true("<td>sp ace</td>" in resp.content)

  def test_describe_view(self):
    resp = self.client.get('/beeswax/table/myview')
    assert_equal(None, resp.context['top_rows'])
    assert_true(resp.context['is_view'])
    assert_true("Beeswax View Metadata" in resp.content)
    assert_true("Drop View" in resp.content)


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


def test_parse_results():
  data = ["foo\tbar", "baz\tboom"]
  assert_equal([["foo", "bar"], ["baz", "boom"]],
    [ x for x in parse_results(data) ])


def test_index_page():
  """Minimal test that index page renders."""
  c = make_logged_in_client()
  c.get("/beeswax")


def test_history_page():
  """
  Exercise the query history view.
  """
  client = make_logged_in_client()

  def do_view(param):
    resp = client.get('/beeswax/query_history?' + param)
    assert_true(len(resp.context['page'].object_list) >= 0)     # Make the query run

  do_view('user=test')
  do_view('user=_all')
  do_view('design_id=1')
  do_view('auto_query=0')
  do_view('auto_query=1')
  do_view('type=hql')
  do_view('type=report')
  do_view('sort=date')
  do_view('sort=-date')
  do_view('sort=state')
  do_view('sort=-state')
  do_view('sort=name')
  do_view('sort=-name')
  do_view('sort=type')
  do_view('sort=-type')
  do_view('sort=name&user=bogus&design_id=1&auto_query=1')
  do_view('sort=-type&user=_all&type=hql&auto_query=0')


def test_strip_trailing_semicolon():
  # Note that there are two queries (both an execute and an explain) scattered
  # in this file that use semicolons all the way through.

  # Single semicolon
  assert_equal("foo", beeswax.views._strip_trailing_semicolon("foo;\n"))
  assert_equal("foo\n", beeswax.views._strip_trailing_semicolon("foo\n;\n\n\n"))
  # Multiple semicolons: strip only last one
  assert_equal("fo;o;", beeswax.views._strip_trailing_semicolon("fo;o;;     "))
  # No semicolons
  assert_equal("foo", beeswax.views._strip_trailing_semicolon("foo"))

def test_hadoop_extraction():
  sample_log = """
Starting Job = job_201003191517_0002, Tracking URL = http://localhost:50030/jobdetails.jsp?jobid=job_201003191517_0002
    --- we should be ignoring duplicates ---
Starting Job = job_201003191517_0002, Tracking URL = http://localhost:50030/jobdetails.jsp?jobid=job_201003191517_0002
Starting Job = job_201003191517_0003, Tracking URL = http://localhost:50030/jobdetails.jsp?jobid=job_201003191517_0003
"""
  assert_equal(["job_201003191517_0002", "job_201003191517_0003"],
    beeswax.views._parse_out_hadoop_jobs(sample_log))
  assert_equal([], beeswax.views._parse_out_hadoop_jobs("nothing to see here"))


def test_hive_site():
  """Test hive-site parsing"""
  HIVE_SITE = """
    <configuration>
      <property>
        <name>hive.metastore.local</name>
        <value>false</value>
      </property>

      <property>
        <name>hive.metastore.uris</name>
        <value>thrift://darkside-1234:9999</value>
      </property>

      <property>
        <name>hive.metastore.warehouse.dir</name>
        <value>/abc</value>
      </property>
    </configuration>
  """

  beeswax.hive_site.reset()
  tmpdir = tempfile.mkdtemp()
  saved = None
  try:
    file(os.path.join(tmpdir, 'hive-site.xml'), 'w').write(HIVE_SITE)

    # We just replace the Beeswax conf variable
    class Getter(object):
      def get(self):
        return tmpdir

    saved = beeswax.conf.BEESWAX_HIVE_CONF_DIR
    beeswax.conf.BEESWAX_HIVE_CONF_DIR = Getter()

    is_local, host, port = beeswax.hive_site.get_metastore()
    assert_false(is_local)
    assert_equal(host, 'darkside-1234')
    assert_equal(port, 9999)
    assert_equal(beeswax.hive_site.get_conf()['hive.metastore.warehouse.dir'], u'/abc')
  finally:
    if saved is not None:
      beeswax.conf.BEESWAX_HIVE_CONF_DIR = saved
    shutil.rmtree(tmpdir)

def test_collapse_whitespace():
  assert_equal("", collapse_whitespace("\t\n\n  \n\t \n"))
  assert_equal("x", collapse_whitespace("\t\nx\n  \n\t \n"))
  assert_equal("x y", collapse_whitespace("\t\nx\n  \ny\t \n"))
