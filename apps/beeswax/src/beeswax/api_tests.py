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
from unittest.mock import Mock, patch

import pytest
from django.test import TestCase
from requests.exceptions import ReadTimeout

from beeswax.api import _autocomplete, _get_functions, _get_sample_data
from desktop.lib.django_test_util import make_logged_in_client
from metastore.conf import ALLOW_SAMPLE_DATA_FROM_VIEWS
from useradmin.models import User

LOG = logging.getLogger()


@pytest.mark.django_db
class TestApi(TestCase):
  def setUp(self):
    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="test")

  def test_autocomplete_time_out(self):
    get_tables_meta = Mock(
      side_effect=ReadTimeout("HTTPSConnectionPool(host='gethue.com', port=10001): Read timed out. (read timeout=120)")
    )
    db = Mock(get_tables_meta=get_tables_meta)

    resp = _autocomplete(db, database="database")

    assert resp == {"code": 500, "error": "HTTPSConnectionPool(host='gethue.com', port=10001): Read timed out. (read timeout=120)"}

  def test_get_functions(self):
    # Mock db.get_functions() to return rows that escape_rows can process
    # Each row should be a list where row[0] is the function name
    db = Mock()
    db.get_functions = Mock(return_value=[["f1"], ["f2"]])  # Return list of rows
    db.client = Mock(query_server={"dialect": "hive"})  # Non-Impala dialect

    resp = _get_functions(db)  # Call the internal function

    assert resp == [{"name": "f1"}, {"name": "f2"}]

  def test_autocomplete_functions(self):
    with patch("beeswax.api._get_functions") as _get_functions:
      db = Mock()
      _get_functions.return_value = [{"name": "f1"}, {"name": "f2"}, {"name": "f3"}]

      resp = _autocomplete(db, database="default", operation="functions")

      assert resp["functions"] == [{"name": "f1"}, {"name": "f2"}, {"name": "f3"}]

  def test_get_function(self):
    db = Mock()
    db.client = Mock(query_server={"dialect": "hive"})
    db.get_function = Mock(
      return_value=[
        ["floor_month(param) - Returns the timestamp at a month granularity"],
        ["param needs to be a timestamp value"],
        ["Example:"],
        ["> SELECT floor_month(CAST('yyyy-MM-dd HH:mm:ss' AS TIMESTAMP)) FROM src;"],
        ["yyyy-MM-01 00:00:00"],
      ]
    )

    data = _autocomplete(db, database="floor_month", operation="function")

    assert data["function"] == {
      "name": "floor_month",
      "signature": "floor_month(param)",
      "description": "Returns the timestamp at a month granularity\nparam needs to be a timestamp value\nExample:\n"
      "> SELECT floor_month(CAST('yyyy-MM-dd HH:mm:ss' AS TIMESTAMP)) FROM src;\nyyyy-MM-01 00:00:00",
    }

    db.client = Mock(query_server={"dialect": "impala"})
    data = _autocomplete(db, operation="function")

    assert data["function"] == {}

  @patch("beeswax.api.dbms.get")
  def test_get_sample_data_for_views(self, dbms_get_mock):
    # Mock the db object that dbms.get() would return
    db_mock = Mock()
    dbms_get_mock.return_value = db_mock

    # Mock table_obj
    table_obj_mock = Mock()
    table_obj_mock.is_view = True
    table_obj_mock.is_impala_only = False  # Assuming not Impala only for simplicity

    db_mock.get_table.return_value = table_obj_mock

    # Scenario 1: allow_sample_data_from_views is False
    cleanup_false = ALLOW_SAMPLE_DATA_FROM_VIEWS.set_for_testing(False)
    self.addCleanup(cleanup_false)

    response_false = _get_sample_data(db_mock, "default_db", "test_view_table", None, None)
    assert response_false["status"] == -1
    assert "Not getting sample data as this is a view" in response_false["message"]

    # Scenario 2: allow_sample_data_from_views is True
    cleanup_true = ALLOW_SAMPLE_DATA_FROM_VIEWS.set_for_testing(True)
    self.addCleanup(cleanup_true)

    # Mock db.get_sample to simulate successful data fetching past the view check
    # We expect it to be called if the view check is passed.
    db_mock.get_sample.return_value = Mock(
      rows=Mock(return_value=[["col1_val", "col2_val"]]),
      cols=Mock(return_value=["col1", "col2"]),
      full_cols=Mock(return_value=[{"name": "col1"}, {"name": "col2"}]),
    )

    response_true = _get_sample_data(db_mock, "default_db", "test_view_table", None, None)
    assert response_true["status"] == 0
    assert "Not getting sample data as this is a view" not in response_true.get("message", "")
    db_mock.get_sample.assert_called_once_with("default_db", table_obj_mock, None, None, generate_sql_only=False, operation=None)
