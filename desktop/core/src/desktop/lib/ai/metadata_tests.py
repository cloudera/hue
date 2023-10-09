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

from nose.tools import assert_true, assert_false, assert_equals, assert_raises

from desktop.lib.ai.metadata import semantic_search

class TestMetadata(object):

  def test_semantic_search(self):
    table_names = ["vendors", "products", "inventory", "offices", "employees"]
    query = "people"

    results = semantic_search(table_names, query, 1)
    assert_equals(len(results), 1)
    assert_equals(results[0], "employees")

    results = semantic_search(table_names, query, 2)
    assert_equals(len(results), 2)

  def test_semantic_search_large_corpus(self):
    table_names = ["orders", "products", "employees", "suppliers", "categories", "claims",
              "policies", "shipments", "payments", "sales", "contacts", "addresses", "accounts",
              "transactions", "users", "messages", "reviews", "comments", "events", "tickets",
              "reservations", "projects", "tasks", "departments", "roles", "permissions", "books",
              "authors", "genres", "students", "courses", "enrollments", "grades",
              "inventory", "locations", "vendors", "partners", "assets", "expenses", "budgets",
              "donations", "hospitals", "patients", "doctors", "appointments", "vehicles",
              "drivers"]

    query = "people"

    results = semantic_search(table_names, query)
    assert_equals(len(results), 10)
    assert_equals(results[0], "users")

    query = "names of people who bought the largest number of books"

    results = semantic_search(table_names, query)
    print("Results :", results)
    assert_true("users" in results, msg="users table must be returned as that contains the name column")
    assert_true("orders" in results)
    assert_true("books" in results)

  def test_semantic_search_large_corpus_tpcds(self):
    table_names  = [
    "call_center - cc_call_center_sk, cc_call_center_id",
    "catalog_page - cp_catalog_page_sk, cp_catalog_page_id, cp_start_date, cp_end_date",
    "catalog_returns - cr_returned_date_sk, cr_returned_time_sk, cr_item_sk, cr_refunded_customer_sk",
    "catalog_sales - cs_sold_date_sk, cs_sold_time_sk, cs_ship_date_sk, cs_item_sk, cs_bill_customer_sk",
    "customer - c_customer_sk, c_customer_id, c_current_cdemo_sk, c_current_hdemo_sk",
    "customer_address - ca_address_sk, ca_address_id",
    "customer_demographics - cd_demo_sk, cd_gender, cd_marital_status",
    "date_dim - d_date_sk, d_date_id, d_date",
    "household_demographics - hd_demo_sk, hd_income_band_sk",
    "income_band - ib_income_band_sk, ib_lower_bound, ib_upper_bound",
    "inventory - inv_date_sk, inv_item_sk",
    "item - i_item_sk, i_item_id",
    "promotion - p_promo_sk, p_promo_id",
    "reason - r_reason_sk, r_reason_id",
    "ship_mode - sm_ship_mode_sk, sm_ship_mode_id",
    "store - s_store_sk, s_store_id",
    "store_returns - sr_returned_date_sk, sr_returned_time_sk, sr_item_sk, sr_customer_sk",
    "store_sales - ss_sold_date_sk, ss_sold_time_sk, ss_item_sk, ss_customer_sk",
    "time_dim - t_time_sk, t_time_id, t_time",
    "warehouse - w_warehouse_sk, w_warehouse_id",
    "web_page - wp_web_page_sk, wp_web_page_id",
    "web_returns - wr_returned_date_sk, wr_returned_time_sk, wr_item_sk, wr_refunded_customer_sk",
    "web_sales - ws_sold_date_sk, ws_sold_time_sk, ws_ship_date_sk, ws_item_sk, ws_bill_customer_sk",
    "web_site - web_site_sk, web_site_id"
    ]


    query = "get year from date_dim, category id and category of items and sum of external store sales price.filter by item manager with id 1 in the year 1998, for the month of december. results should be sorted in descending order of the total external sales price, with a secondary sort on year, category id, and product category. limit the output to 100 rows."

    results = semantic_search(table_names, query, 10)
    table_results = [result.split(" - ")[0] for result in results]
    print("Table Names:", table_results)
    print("Results :", results)
    assert_true("date_dim" in table_results, msg="users table must be returned as that contains the name column")
    assert_true("store_sales" in table_results)
    assert_true("item" in table_results)

    
  def test_semantic_search_large_corpus_poorly_named_tables(self):
      table_names  = [
      "call_center - cc_call_center_sk, cc_call_center_id",
      "catalog_page - cp_catalog_page_sk, cp_catalog_page_id, cp_start_date, cp_end_date",
      "catalog_returns - cr_returned_date_sk, cr_returned_time_sk, cr_item_sk, cr_refunded_customer_sk",
      "catalog_sales - cs_sold_date_sk, cs_sold_time_sk, cs_ship_date_sk, cs_item_sk, cs_bill_customer_sk",
      "customer - c_customer_sk, c_customer_id, c_current_cdemo_sk, c_current_hdemo_sk",
      "customer_address - ca_address_sk, ca_address_id",
      "customer_demographics - cd_demo_sk, cd_gender, cd_marital_status",
      "date_dim - d_date_sk, d_date_id, d_date",
      "household_demographics - hd_demo_sk, hd_income_band_sk",
      "income_band - ib_income_band_sk, ib_lower_bound, ib_upper_bound",
      "inventory - inv_date_sk, inv_item_sk",
      "item - i_item_sk, i_item_id",
      "promotion - p_promo_sk, p_promo_id",
      "reason - r_reason_sk, r_reason_id",
      "ship_mode - sm_ship_mode_sk, sm_ship_mode_id",
      "store - s_store_sk, s_store_id",
      "store_returns - sr_returned_date_sk, sr_returned_time_sk, sr_item_sk, sr_customer_sk",
      "store_sales - ss_sold_date_sk, ss_sold_time_sk, ss_item_sk, ss_customer_sk",
      "time_dim - t_time_sk, t_time_id, t_time",
      "warehouse - w_warehouse_sk, w_warehouse_id",
      "web_page - wp_web_page_sk, wp_web_page_id",
      "web_returns - wr_returned_date_sk, wr_returned_time_sk, wr_item_sk, wr_refunded_customer_sk",
      "web_sales - ws_sold_date_sk, ws_sold_time_sk, ws_ship_date_sk, ws_item_sk, ws_bill_customer_sk",
      "web_site - web_site_sk, web_site_id",
      "sample_99 - employee_id, employee_name"
      ]


      query = "get top 5 employees"

      results = semantic_search(table_names, query, 10)
      table_results = [result.split(" - ")[0] for result in results]
      print("Table Names:", table_results)
      print("Results :", results)
      assert_true("sample_99" in table_results, msg="users table must be returned as that contains the name column")