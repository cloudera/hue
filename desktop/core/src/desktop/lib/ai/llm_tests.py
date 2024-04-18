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

import dataclasses
import logging
# Assuming that 'desktop' is a directory at the same level as this file
from desktop.lib.ai.sql import perform_sql_task
from desktop.api_public import get_django_request
from unittest.mock import patch
from desktop.settings import BASE_DIR
from notebook.api import TableReader
from unittest.mock import Mock
import json
LOG = logging.getLogger(__name__)

generate_scenarios = [
  {
    "scenario": "Generate",
    "sql": "",
    "input": "get store name, store id, manager, zipcode,total sales of each store and sort by total sales in ascending order.",
    "expected_response": {
     "sql": "select",
     "warning": False,
     "summary": False,
     "semanticerror": False,
     "sqlerror": False,
     "summary": False,
     "explain": False
    }
  },
  {
    "scenario": "Generate 2",
    "sql": "",
    "input": "give me all customer names that bought stuff in april 2021",
    "expected_response": {
     "sql": "select",
     "warning": False,
     "summary": False,
     "semanticerror": False,
     "sqlerror": False,
     "explain": False
    }
  },
  # {
  #   "scenario": "Delete Statement",
  #   "sql": "",
  #   "input": "Delete the 5 least profitable stores",
  #   "expected_response": {
  #    "sql": "delete",
  #    "warning": True,
  #    "summary": False,
  #    "semanticerror": False,
  #    "sqlerror": False,
  #    "explain": False
  #   }
  # },
  {
    "scenario": "Semantic Error",
    "sql": "",
    "input": "wqepwrf tpoiejr iofpjqpo iwgj ipto",
    "expected_response": {
     "sql": "",
     "warning": False,
     "semanticerror": True,
     "sqlerror": False,
     "explain": False
    }
  },
  
]


edit_scenarios = [
  {
    "scenario": "Edit Verify",
    "input": "add sales per employee and sort by sales per employee where sales per employee is total sales by number of employees",
    "sql": "/* NQL: get store name, store id, manager, zipcode,total sales of each store and sort by \ntotal sales in ascending order. */\nSELECT\n  s.s_store_name,\n  s.s_store_id,\n  s.s_manager,\n  s.s_zip,\n  SUM(ss.ss_ext_sales_price) AS total_sales\nFROM\n  store s\n  JOIN store_sales ss ON s.s_store_sk = ss.ss_store_sk\nGROUP BY\n  s.s_store_name,\n  s.s_store_id,\n  s.s_manager,\n  s.s_zip\nORDER BY\n  total_sales ASC;",
    "expected_response": {
     "sql": "select",
     "warning": False,
     "sqlrror": False,
     "summary": False
    }
  }
]

optimize_scenarios = [
  {
    "scenario": "Optimize inner select",
    "sql": "/* NQL: get store name, store id, manager, zipcode,total sales of each store and sort by \ntotal sales in ascending order. */\nSELECT\n  s.s_store_name,\n  s.s_store_id,\n  s.s_manager,\n  s.s_zip,\n  SUM(ss.ss_ext_sales_price) AS total_sales\nFROM\n  store s\n  JOIN store_sales ss ON s.s_store_sk = ss.ss_store_sk\nGROUP BY\n  s.s_store_name,\n  s.s_store_id,\n  s.s_manager,\n  s.s_zip\nORDER BY\n  total_sales ASC;",
    "input": "",
    "expected_response": {
     "no_of_select": 1,
     "sql": "",
     "warning": False,
     "sqlError": False,
     "summary": False
    }
  },
]

@patch('desktop.lib.ai.sql.TableReader')
def test_perform_sql_task(mock_table_reader):
  def run_scenario(scenario, task):
    # Read the JSON data from the file
    with open(BASE_DIR + '/desktop/core/src/desktop/lib/ai/tables.json', 'rb') as file:
      tables_metadata = json.load(file)

    request = Mock()
    inputJson = {
      "task": task,
      "sql": scenario["sql"],
      "input": scenario['input'],
      "dialect": "hive",
      "metadata": {
        "tables": tables_metadata
      }
    }
    task = inputJson["task"]
    input = inputJson["input"]
    sql_query = inputJson["sql"]
    dialect = inputJson["dialect"]
    metadata = inputJson["metadata"]
    mock_table_reader.return_value.execute.return_value = ''
    mock_table_reader.return_value.__iter__.return_value = iter([])  
    response = perform_sql_task(request, task, input, sql_query, dialect, metadata)

    response_dict = dataclasses.asdict(response)
    sql_response = response_dict.get('sql', '').strip().lower()

    check_warning(response_dict, scenario["expected_response"], "warning")
    check_warning(response_dict, scenario["expected_response"], "summary")
    check_warning(response_dict, scenario["expected_response"], "semanticerror")
    check_warning(response_dict, scenario["expected_response"], "sqlerror")
    check_warning(response_dict, scenario["expected_response"], "explain")
    if(("no_of_select" in scenario["expected_response"]) and scenario["expected_response"]["no_of_select"]):
      # Count the occurrences of the "SELECT" keyword
      select_count = sql_response.count("select")
      assert scenario["expected_response"]["no_of_select"] is select_count, "SQL is not optimized"

    assert scenario["expected_response"]["sql"] in sql_response, "SQL does not contain a SELECT statement"

  # Loop through each test scenario
  for scenario in generate_scenarios:
    run_scenario(scenario, "generate")

  for scenario in edit_scenarios:
    run_scenario(scenario, "edit")

  for scenario in optimize_scenarios:
    run_scenario(scenario, "optimize")


def check_warning(response, expected_response, keyName):
  if keyName in response and keyName in expected_response:
    if expected_response[keyName] is False:
      assert response[keyName] in [None, False, ""], f"Mismatch in warning: {keyName}"
    else:
      assert response[keyName] not in [None, False, ""], f"Different Than Expected: {keyName}"
