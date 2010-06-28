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
#

"""
Tests for report generator
"""

from nose.tools import assert_true, assert_equal

from desktop.lib.django_test_util import assert_equal_mod_whitespace
from desktop.lib.django_test_util import assert_similar_pages
from beeswax.test_base import wait_for_query_to_finish, verify_history, BeeswaxSampleProvider

from beeswax.report.report_gen import BooleanCondition, ColumnSelection
from beeswax.report.report_gen import QTable, ConstSelection, LogicalUnion

import beeswax.models

def test_report_gen_query():
  """
  Tests HQL generation backend
  """
  # Table manifest
  table = QTable('test_table')
  assert_equal_mod_whitespace(table.manifest(is_from=False), 'test_table')
  assert_equal_mod_whitespace(table.manifest(is_from=True), 'test_table')
  table.alias = 'foo'
  assert_equal_mod_whitespace(table.manifest(is_from=False), 'foo')
  assert_equal_mod_whitespace(table.manifest(is_from=True), 'test_table foo')

  # Column manifest
  col = ColumnSelection(table, 'col')
  assert_equal_mod_whitespace(col.manifest(), 'foo.col')
  assert_equal_mod_whitespace(col.manifest(is_select=True), 'foo.col')
  assert_equal_mod_whitespace(col.manifest(is_sort=True), 'foo.col')
  col.alias = 'X'
  assert_equal_mod_whitespace(col.manifest(), 'foo.col')
  assert_equal_mod_whitespace(col.manifest(is_select=True), 'foo.col AS X')
  assert_equal_mod_whitespace(col.manifest(is_sort=True), 'X')

  # Const manifest
  simple_int = ConstSelection('69')
  simple_int.alias = 'INT'
  assert_equal_mod_whitespace(simple_int.manifest(), '69')

  konst = ConstSelection('quote-"')
  assert_equal_mod_whitespace(konst.manifest(), '"quote-\\""')
  assert_equal_mod_whitespace(konst.manifest(is_select=True), '"quote-\\""')
  konst.alias = 'Y'
  assert_equal_mod_whitespace(konst.manifest(), '"quote-\\""')
  assert_equal_mod_whitespace(konst.manifest(is_select=True), '"quote-\\"" AS Y')

  # Boolean condition manifest
  bool_cond = BooleanCondition(col, '<>', konst)
  assert_true(not bool_cond.is_joinable())
  assert_equal_mod_whitespace(bool_cond.manifest(), 'foo.col <> "quote-\\""')

  union_root = LogicalUnion('AND')
  union_root.add_cond(bool_cond)
  assert_equal_mod_whitespace(union_root.manifest(), '( foo.col <> "quote-\\"" )')
  union_root.compact()
  assert_equal_mod_whitespace(union_root.manifest(), '( foo.col <> "quote-\\"" )')
  union_root.add_cond(BooleanCondition(simple_int, '=', simple_int))
  assert_equal_mod_whitespace(union_root.manifest(), '( foo.col <> "quote-\\"" AND 69 = 69 )')

  union_sub = LogicalUnion('OR')
  union_sub.add_cond(BooleanCondition(col, 'IS NULL'))
  union_root.add_subunion(union_sub)
  assert_equal(union_root.size(), 3)
  assert_equal_mod_whitespace(union_root.manifest(),
                            '( foo.col <> "quote-\\"" AND 69 = 69 AND ( foo.col IS NULL ) )')

  # Test union compaction
  dumb_union = LogicalUnion('AND')
  dumb_union.add_subunion(union_root)
  assert_equal_mod_whitespace(dumb_union.manifest(),
                            '( ( foo.col <> "quote-\\"" AND 69 = 69 AND ( foo.col IS NULL ) ) )')
  dumb_union.compact()
  assert_equal_mod_whitespace(dumb_union.manifest(),
                            '( foo.col <> "quote-\\"" AND 69 = 69 AND ( foo.col IS NULL ) )')


class TestReportGenWithHadoop(BeeswaxSampleProvider):
  """Tests for report generator that require a running Hadoop"""
  requires_hadoop = True

  def test_report_gen_view(self):
    """
    Test report gen view logic and query generation.
    It requires Hive because report gen automatically gathers all the table names.
    """
    cli = self.client

    resp = cli.get('/beeswax/report_gen')
    assert_true(resp.status_code, 200)

    # This generates a SELECT * and takes us to the execute page
    resp = cli.post("/beeswax/report_gen", {
      'columns-next_form_id':     '1',
      'columns-0-_exists':       'True',
      'columns-0-col':           '*',
      'columns-0-display':       'on',
      'columns-0-source':        'table',
      'columns-0-table':         'test',
      'union.conds-next_form_id': '0',
      'union.bool-bool':          'AND',
      'union.mgmt-next_form_id':  '0',
      'button-advanced':          'Submit',
    })
    assert_equal_mod_whitespace(r"SELECT test.* FROM test",
                                resp.context["form"].query.initial["query"])

    # Add a new column
    resp = cli.post("/beeswax/report_gen", {
      'columns-add':                  'True',
      'columns-next_form_id':         '1',
      'columns-0-_exists':            'True',
      'union.bool-bool':              'AND',
      'union.conds-next_form_id':     '1',
      'union.conds-0-_exists':        'True',
      'union.conds-0-op':             '=',
      'union.mgmt-next_form_id':      '0'
    })
    assert_true('columns-1-_exists' in resp.content)

    # Remove a sub form
    resp = cli.post("/beeswax/report_gen", {
      'columns-next_form_id':          '1',
      'columns-0-_exists':             'True',
      'union.bool-bool':               'AND',
      'union.conds-next_form_id':      '1',
      'union.conds-0-_exists':         'True',
      'union.mgmt-next_form_id':       '1',
      'union.sub0.bool-bool':          'AND',
      'union.sub0.conds-next_form_id': '1',
      'union.sub0.conds-0-_exists':    'True',
      'union.sub0.mgmt-next_form_id':  '0',
      'union.sub0.mgmt-remove':        'True'
    })
    assert_true('union.sub0' not in resp.content)

    # This generates a SELECT * and directly submits the query
    resp = cli.post("/beeswax/report_gen", {
      'columns-next_form_id':     '1',
      'columns-0-_exists':        'True',
      'columns-0-col':            '*',
      'columns-0-display':        'on',
      'columns-0-source':         'table',
      'columns-0-table':          'test',
      'union.conds-next_form_id': '0',
      'union.bool-bool':          'AND',
      'union.mgmt-next_form_id':  '0',
      'button-submit':            'Submit',
      'saveform-name':            'select star via report',
      'saveform-save':            'True',
    }, follow=True)
    resp = wait_for_query_to_finish(self.client, resp, max=30.0)
    # Note that it may not return all rows at once. But we expect at least 10.
    assert_true(len(resp.context['results']) > 10)

    verify_history(cli, fragment='SELECT test.*', design='select star via report')


  def test_report_designs(self):
    """Test report design view and interaction"""
    cli = self.client

    # Test report design auto-save and loading
    resp = cli.post("/beeswax/report_gen", {
      'columns-next_form_id':           '1',
      'columns-0-_exists':              'True',
      'union.conds-next_form_id':       '0',
      'union.mgmt-next_form_id':        '1',
      'union.sub0.bool-bool':           'AND',
      'union.sub0.conds-next_form_id':  '1',
      'union.sub0.conds-0-_exists':     'True',
      'union.sub0.mgmt-next_form_id':   '0',
      'button-submit':                  'Submit',
      'saveform-name':                  'reporter',
      'saveform-save':                  'True',
    })

    # The report above is invalid. But it saves and submit at the same time.
    design = beeswax.models.SavedQuery.objects.filter(name='reporter')[0]
    resp2 = cli.get('/beeswax/report_gen/%s' % (design.id,))
    assert_similar_pages(resp.content, resp2.content)
