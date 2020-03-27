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

import logging
import sys

from celery import states
from nose.tools import assert_equal, assert_not_equal, assert_true, assert_false

from desktop.lib.django_test_util import make_logged_in_client
from useradmin.models import User

from notebook.connectors.sql_alchemy import SqlAlchemyApi
from notebook.tasks import run_sync_query, download_to_file, close_statement, get_log

if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock, MagicMock
else:
  from mock import patch, Mock, MagicMock


LOG = logging.getLogger(__name__)



class TestRunAsyncQueryTask():

  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="test")


  def test_run_query_only(self):
    with patch('notebook.tasks._get_request') as _get_request:
      with patch('notebook.tasks.get_api') as get_api:
        with patch('notebook.tasks.DataAdapter') as DataAdapter:
          with patch('notebook.tasks.export_csvxls.create_generator') as create_generator:
            with patch('notebook.tasks.caches') as caches:

              content_generator = MagicMock(row_counter=2)
              content_generator.__iter__.return_value = [('col1', [[1]]), ('col2', [[2]])]
              DataAdapter.return_value = content_generator

              get_api.return_value = Mock(
                check_status=Mock(return_value={'status': 0})
              )

              def notebook_dict(key):
                return {
                  'uuid': '1ca47e0d-4708-4709-82c1-a9280e15452b',
                }.get(key, Mock())
              notebook = MagicMock()
              notebook.__getitem__.side_effect = notebook_dict
              snippet = MagicMock()

              meta = download_to_file(notebook, snippet)

              assert_equal(meta['row_counter'], 2, meta)


  def test_close_statement(self):
    with patch('notebook.tasks._get_request') as _get_request:
      with patch('notebook.tasks.download_to_file') as download_to_file:
        with patch('notebook.tasks.close_statement_async') as close_statement_async:
          with patch('notebook.tasks.caches') as caches:

            download_to_file.AsyncResult.return_value = Mock(
              state=states.SUCCESS
            )

            def notebook_dict(key):
              return {
                'uuid': '1ca47e0d-4708-4709-82c1-a9280e15452b',
              }.get(key, Mock())
            notebook = MagicMock()
            notebook.__getitem__.side_effect = notebook_dict
            snippet = MagicMock()

            response = close_statement(notebook, snippet)

            assert_equal(response, {'status': 0})


  def test_get_log(self):
    with patch('notebook.tasks._get_request') as _get_request:
      with patch('notebook.tasks.download_to_file') as download_to_file:

        download_to_file.AsyncResult.return_value = Mock(
          state=states.SUCCESS
        )

        def notebook_dict(key):
          return {
            'uuid': '1ca47e0d-4708-4709-82c1-a9280e15452b',
          }.get(key, Mock())
        notebook = MagicMock()
        notebook.__getitem__.side_effect = notebook_dict
        snippet = MagicMock()

        response = get_log(notebook, snippet, startFrom=None, size=None, postdict=None, user_id=None)

        assert_equal(response, '')



class TestRunSyncQueryTask():

  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="test")


  def test_run_query(self):
    snippet = {'type': 'mysql', 'statement_raw': 'SHOW TABLES', 'variables': []}

    with patch('notebook.tasks.Document2.objects.get_by_uuid') as get_by_uuid:
      with patch('notebook.tasks.Notebook.get_data') as get_data:
        with patch('notebook.tasks.make_notebook') as make_notebook:
          with patch('notebook.tasks.download_to_file') as download_to_file:

            get_data.return_value = {'snippets': [snippet]}
            make_notebook.return_value = Mock(
              execute=Mock(
                return_value={'history_uuid': '1'}
              )
            )
            download_to_file.AsyncResult.return_value = Mock(
              state=states.SUCCESS
            )
            query = Mock()

            task = run_sync_query(query, self.user)

            assert_equal(task, {'history_uuid': '1', 'uuid': '1'})
