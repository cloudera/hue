from nose.tools import assert_true, assert_false, assert_equals, assert_raises
import pdb
import dataclasses
import logging
# Assuming that 'desktop' is a directory at the same level as this file
from .sql import TaskType, SQLResponse, perform_sql_task
# from .sql import sql
import json
from desktop.lib.django_util import JsonResponse
LOG = logging.getLogger(__name__)

tables_metadata = [
  {
    "name": "store_sales",
    "columns": [
      {
        "name": "ss_sold_date_sk",
        "type": "bigint",
        "comment": "",
        "index": 0
      },
      {
        "name": "ss_sold_time_sk",
        "type": "bigint",
        "comment": "",
        "index": 1
      },
      {
        "name": "ss_item_sk",
        "type": "bigint",
        "comment": "",
        "index": 2
      },
      {
        "name": "ss_customer_sk",
        "type": "bigint",
        "comment": "",
        "index": 3
      },
      {
        "name": "ss_cdemo_sk",
        "type": "bigint",
        "comment": "",
        "index": 4
      },
      {
        "name": "ss_hdemo_sk",
        "type": "bigint",
        "comment": "",
        "index": 5
      },
      {
        "name": "ss_addr_sk",
        "type": "bigint",
        "comment": "",
        "index": 6
      },
      {
        "name": "ss_store_sk",
        "type": "bigint",
        "comment": "",
        "index": 7
      },
      {
        "name": "ss_promo_sk",
        "type": "bigint",
        "comment": "",
        "index": 8
      },
      {
        "name": "ss_ticket_number",
        "type": "bigint",
        "comment": "",
        "index": 9
      },
      {
        "name": "ss_quantity",
        "type": "int",
        "comment": "",
        "index": 10
      },
      {
        "name": "ss_wholesale_cost",
        "type": "decimal(7,2)",
        "comment": "",
        "index": 11
      },
      {
        "name": "ss_list_price",
        "type": "decimal(7,2)",
        "comment": "",
        "index": 12
      },
      {
        "name": "ss_sales_price",
        "type": "decimal(7,2)",
        "comment": "",
        "index": 13
      },
      {
        "name": "ss_ext_discount_amt",
        "type": "decimal(7,2)",
        "comment": "",
        "index": 14
      },
      {
        "name": "ss_ext_sales_price",
        "type": "decimal(7,2)",
        "comment": "",
        "index": 15
      },
      {
        "name": "ss_ext_wholesale_cost",
        "type": "decimal(7,2)",
        "comment": "",
        "index": 16
      },
      {
        "name": "ss_ext_list_price",
        "type": "decimal(7,2)",
        "comment": "",
        "index": 17
      },
      {
        "name": "ss_ext_tax",
        "type": "decimal(7,2)",
        "comment": "",
        "index": 18
      },
      {
        "name": "ss_coupon_amt",
        "type": "decimal(7,2)",
        "comment": "",
        "index": 19
      },
      {
        "name": "ss_net_paid",
        "type": "decimal(7,2)",
        "comment": "",
        "index": 20
      },
      {
        "name": "ss_net_paid_inc_tax",
        "type": "decimal(7,2)",
        "comment": "",
        "index": 21
      },
      {
        "name": "ss_net_profit",
        "type": "decimal(7,2)",
        "comment": "",
        "index": 22
      }
    ]
  },
  {
    "name": "date_dim",
    "columns": [
      {
        "name": "d_date_sk",
        "type": "bigint",
        "comment": "",
        "index": 0
      },
      {
        "name": "d_date_id",
        "type": "char(16)",
        "comment": "",
        "index": 1
      },
      {
        "name": "d_date",
        "type": "date",
        "comment": "",
        "index": 2
      },
      {
        "name": "d_month_seq",
        "type": "int",
        "comment": "",
        "index": 0
      },
      {
        "name": "d_week_seq",
        "type": "int",
        "comment": "",
        "index": 4
      },
      {
        "name": "d_quarter_seq",
        "type": "int",
        "comment": "",
        "index": 5
      },
      {
        "name": "d_year",
        "type": "int",
        "comment": "",
        "index": 6
      },
      {
        "name": "d_dow",
        "type": "int",
        "comment": "",
        "index": 7
      },
      {
        "name": "d_moy",
        "type": "int",
        "comment": "",
        "index": 8
      },
      {
        "name": "d_dom",
        "type": "int",
        "comment": "",
        "index": 9
      },
      {
        "name": "d_qoy",
        "type": "int",
        "comment": "",
        "index": 10
      },
      {
        "name": "d_fy_year",
        "type": "int",
        "comment": "",
        "index": 11
      },
      {
        "name": "d_fy_quarter_seq",
        "type": "int",
        "comment": "",
        "index": 12
      },
      {
        "name": "d_fy_week_seq",
        "type": "int",
        "comment": "",
        "index": 13
      },
      {
        "name": "d_day_name",
        "type": "char(9)",
        "comment": "",
        "index": 14
      },
      {
        "name": "d_quarter_name",
        "type": "char(6)",
        "comment": "",
        "index": 15
      },
      {
        "name": "d_holiday",
        "type": "char(1)",
        "comment": "",
        "index": 16
      },
      {
        "name": "d_weekend",
        "type": "char(1)",
        "comment": "",
        "index": 17
      },
      {
        "name": "d_following_holiday",
        "type": "char(1)",
        "comment": "",
        "index": 18
      },
      {
        "name": "d_first_dom",
        "type": "int",
        "comment": "",
        "index": 19
      },
      {
        "name": "d_last_dom",
        "type": "int",
        "comment": "",
        "index": 20
      },
      {
        "name": "d_same_day_ly",
        "type": "int",
        "comment": "",
        "index": 21
      },
      {
        "name": "d_same_day_lq",
        "type": "int",
        "comment": "",
        "index": 22
      },
      {
        "name": "d_current_day",
        "type": "char(1)",
        "comment": "",
        "index": 23
      },
      {
        "name": "d_current_week",
        "type": "char(1)",
        "comment": "",
        "index": 24
      },
      {
        "name": "d_current_month",
        "type": "char(1)",
        "comment": "",
        "index": 25
      },
      {
        "name": "d_current_quarter",
        "type": "char(1)",
        "comment": "",
        "index": 26
      },
      {
        "name": "d_current_year",
        "type": "char(1)",
        "comment": "",
        "index": 27
      }
    ]
  },
  {
    "name": "customer",
    "columns": [
      {
        "name": "c_customer_sk",
        "type": "bigint",
        "comment": "",
        "index": 0
      },
      {
        "name": "c_customer_id",
        "type": "char(16)",
        "comment": "",
        "index": 1
      },
      {
        "name": "c_current_cdemo_sk",
        "type": "bigint",
        "comment": "",
        "index": 2
      },
      {
        "name": "c_current_hdemo_sk",
        "type": "bigint",
        "comment": "",
        "index": 3
      },
      {
        "name": "c_current_addr_sk",
        "type": "bigint",
        "comment": "",
        "index": 4
      },
      {
        "name": "c_first_shipto_date_sk",
        "type": "bigint",
        "comment": "",
        "index": 5
      },
      {
        "name": "c_first_sales_date_sk",
        "type": "bigint",
        "comment": "",
        "index": 6
      },
      {
        "name": "c_salutation",
        "type": "char(10)",
        "comment": "",
        "index": 7
      },
      {
        "name": "c_first_name",
        "type": "char(20)",
        "comment": "",
        "index": 8
      },
      {
        "name": "c_last_name",
        "type": "char(30)",
        "comment": "",
        "index": 9
      },
      {
        "name": "c_preferred_cust_flag",
        "type": "char(1)",
        "comment": "",
        "index": 10
      },
      {
        "name": "c_birth_day",
        "type": "int",
        "comment": "",
        "index": 11
      },
      {
        "name": "c_birth_month",
        "type": "int",
        "comment": "",
        "index": 12
      },
      {
        "name": "c_birth_year",
        "type": "int",
        "comment": "",
        "index": 13
      },
      {
        "name": "c_birth_country",
        "type": "varchar(20)",
        "comment": "",
        "index": 14
      },
      {
        "name": "c_login",
        "type": "char(13)",
        "comment": "",
        "index": 15
      },
      {
        "name": "c_email_address",
        "type": "char(50)",
        "comment": "",
        "index": 16
      },
      {
        "name": "c_last_review_date_sk",
        "type": "bigint",
        "comment": "",
        "index": 17
      }
    ]
  },
  {
    "name": "store",
    "columns": [
      {
        "name": "s_store_sk",
        "type": "bigint",
        "comment": "",
        "index": 0
      },
      {
        "name": "s_store_id",
        "type": "char(16)",
        "comment": "",
        "index": 1
      },
      {
        "name": "s_rec_start_date",
        "type": "date",
        "comment": "",
        "index": 2
      },
      {
        "name": "s_rec_end_date",
        "type": "date",
        "comment": "",
        "index": 3
      },
      {
        "name": "s_closed_date_sk",
        "type": "bigint",
        "comment": "",
        "index": 4
      },
      {
        "name": "s_store_name",
        "type": "varchar(50)",
        "comment": "",
        "index": 5
      },
      {
        "name": "s_number_employees",
        "type": "int",
        "comment": "",
        "index": 6
      },
      {
        "name": "s_floor_space",
        "type": "int",
        "comment": "",
        "index": 7
      },
      {
        "name": "s_hours",
        "type": "char(20)",
        "comment": "",
        "index": 8
      },
      {
        "name": "s_manager",
        "type": "varchar(40)",
        "comment": "",
        "index": 9
      },
      {
        "name": "s_market_id",
        "type": "int",
        "comment": "",
        "index": 10
      },
      {
        "name": "s_geography_class",
        "type": "varchar(100)",
        "comment": "",
        "index": 11
      },
      {
        "name": "s_market_desc",
        "type": "varchar(100)",
        "comment": "",
        "index": 12
      },
      {
        "name": "s_market_manager",
        "type": "varchar(40)",
        "comment": "",
        "index": 13
      },
      {
        "name": "s_division_id",
        "type": "int",
        "comment": "",
        "index": 14
      },
      {
        "name": "s_division_name",
        "type": "varchar(50)",
        "comment": "",
        "index": 15
      },
      {
        "name": "s_company_id",
        "type": "int",
        "comment": "",
        "index": 16
      },
      {
        "name": "s_company_name",
        "type": "varchar(50)",
        "comment": "",
        "index": 17
      },
      {
        "name": "s_street_number",
        "type": "varchar(10)",
        "comment": "",
        "index": 18
      },
      {
        "name": "s_street_name",
        "type": "varchar(60)",
        "comment": "",
        "index": 19
      },
      {
        "name": "s_street_type",
        "type": "char(15)",
        "comment": "",
        "index": 20
      },
      {
        "name": "s_suite_number",
        "type": "char(10)",
        "comment": "",
        "index": 21
      },
      {
        "name": "s_city",
        "type": "varchar(60)",
        "comment": "",
        "index": 22
      },
      {
        "name": "s_county",
        "type": "varchar(30)",
        "comment": "",
        "index": 23
      },
      {
        "name": "s_state",
        "type": "char(2)",
        "comment": "",
        "index": 24
      },
      {
        "name": "s_zip",
        "type": "char(10)",
        "comment": "",
        "index": 25
      },
      {
        "name": "s_country",
        "type": "varchar(20)",
        "comment": "",
        "index": 26
      },
      {
        "name": "s_gmt_offset",
        "type": "decimal(5,2)",
        "comment": "",
        "index": 27
      },
      {
        "name": "s_tax_percentage",
        "type": "decimal(5,2)",
        "comment": "",
        "index": 28
      }
    ]
  },
  {
    "name": "item",
    "columns": [
      {
        "name": "i_item_sk",
        "type": "bigint",
        "comment": "",
        "index": 0
      },
      {
        "name": "i_item_id",
        "type": "char(16)",
        "comment": "",
        "index": 1
      },
      {
        "name": "i_rec_start_date",
        "type": "date",
        "comment": "",
        "index": 2
      },
      {
        "name": "i_rec_end_date",
        "type": "date",
        "comment": "",
        "index": 3
      },
      {
        "name": "i_item_desc",
        "type": "varchar(200)",
        "comment": "",
        "index": 4
      },
      {
        "name": "i_current_price",
        "type": "decimal(7,2)",
        "comment": "",
        "index": 5
      },
      {
        "name": "i_wholesale_cost",
        "type": "decimal(7,2)",
        "comment": "",
        "index": 6
      },
      {
        "name": "i_brand_id",
        "type": "int",
        "comment": "",
        "index": 7
      },
      {
        "name": "i_brand",
        "type": "char(50)",
        "comment": "",
        "index": 8
      },
      {
        "name": "i_class_id",
        "type": "int",
        "comment": "",
        "index": 9
      },
      {
        "name": "i_class",
        "type": "char(50)",
        "comment": "",
        "index": 10
      },
      {
        "name": "i_category_id",
        "type": "int",
        "comment": "",
        "index": 11
      },
      {
        "name": "i_category",
        "type": "char(50)",
        "comment": "",
        "index": 12
      },
      {
        "name": "i_manufact_id",
        "type": "int",
        "comment": "",
        "index": 13
      },
      {
        "name": "i_manufact",
        "type": "char(50)",
        "comment": "",
        "index": 14
      },
      {
        "name": "i_size",
        "type": "char(20)",
        "comment": "",
        "index": 15
      },
      {
        "name": "i_formulation",
        "type": "char(20)",
        "comment": "",
        "index": 16
      },
      {
        "name": "i_color",
        "type": "char(20)",
        "comment": "",
        "index": 17
      },
      {
        "name": "i_units",
        "type": "char(10)",
        "comment": "",
        "index": 18
      },
      {
        "name": "i_container",
        "type": "char(10)",
        "comment": "",
        "index": 19
      },
      {
        "name": "i_manager_id",
        "type": "int",
        "comment": "",
        "index": 20
      },
      {
        "name": "i_product_name",
        "type": "char(50)",
        "comment": "",
        "index": 21
      }
    ]
  },
]

generate_scenarios = [
    # {
    #     "scenario": "Generate",
    #     "sql": "",
    #     "input": "get store name, store id, manager, zipcode,total sales of each store and sort by total sales in ascending order.",
    #     "expected_response": {
    #        "sql": "select",
    #        "warning": False,
    #        "summary": False,
    #        "semanticerror": False,
    #        "sqlerror": False,
    #        "summary": False,
    #        "explain": False
    #     }
    # },
    # {
    #     "scenario": "Generate 2",
    #     "sql": "",
    #     "input": "give me all customer names that bought stuff in april 2021",
    #     "expected_response": {
    #        "sql": "select",
    #        "warning": False,
    #        "summary": False,
    #        "semanticerror": False,
    #        "sqlerror": False,
    #        "explain": False
    #     }
    # },
    # {
    #     "scenario": "Delete Statement",
    #     "sql": "",
    #     "input": "Delete the 5 least profitable stores",
    #     "expected_response": {
    #        "sql": "delete",
    #        "warning": True,
    #        "summary": False,
    #        "semanticerror": False,
    #        "sqlerror": False,
    #        "explain": False
    #     }
    # },
    # {
    #     "scenario": "Semantic Error",
    #     "sql": "",
    #     "input": "wqepwrf tpoiejr iofpjqpo iwgj ipto",
    #     "expected_response": {
    #        "sql": "",
    #        "warning": False,
    #        "semanticerror": True,
    #        "sqlerror": False,
    #        "explain": False
    #     }
    # },
    
]


edit_scenarios = [
    {
        "scenario": "Edit Verify",
        "input": "add sales per employee and sort by sales per employee where sales per employee is total sales by number of employees",
        "sql": "/* NQL: get store name, store id, manager, zipcode,total sales of each store and sort by \ntotal sales in ascending order. */\nSELECT\n  s.s_store_name,\n  s.s_store_id,\n  s.s_manager,\n  s.s_zip,\n  SUM(ss.ss_ext_sales_price) AS total_sales\nFROM\n  store s\n  JOIN store_sales ss ON s.s_store_sk = ss.ss_store_sk\nGROUP BY\n  s.s_store_name,\n  s.s_store_id,\n  s.s_manager,\n  s.s_zip\nORDER BY\n  total_sales ASC;",
        "expected_response": {
           "sql": "select",
           "warning": False,
           "sqlerror": False,
           "summary": False
        }
    }
]

optimize_scenatios = [
    #    {
    #     "scenario": "Optimize inner select",
    #     "sql": "/* NQL: get store name, store id, manager, zipcode,total sales of each store and sort by \ntotal sales in ascending order. */\nSELECT\n  s.s_store_name,\n  s.s_store_id,\n  s.s_manager,\n  s.s_zip,\n  SUM(ss.ss_ext_sales_price) AS total_sales\nFROM\n  store s\n  JOIN store_sales ss ON s.s_store_sk = ss.ss_store_sk\nGROUP BY\n  s.s_store_name,\n  s.s_store_id,\n  s.s_manager,\n  s.s_zip\nORDER BY\n  total_sales ASC;",
    #     "expected_response": {
    #        "no_of_select": 1,
    #        "warning": False,
    #        "sqlError": False,
    #        "summary": False
    #     }
    # },
]


def test_perform_sql_task():
    # pdb.set_trace()

        # Loop through each test scenario
    for scenario in generate_scenarios:
      inputJson = {
        "task": "generate",
        "sql": scenario["sql"],
        "input": scenario['input'],
        "dialect": "hive",
        "metadata": {
          "tables": tables_metadata
        }
        }
      task = inputJson["task"]
      input = inputJson["input"]
      sql_query =  inputJson["sql"]
      dialect = inputJson["dialect"]
      metadata = inputJson["metadata"]


      # Call the function
      response = perform_sql_task(task, input, sql_query, dialect, metadata)

      # Convert SQLResponse to dictionary
      response_dict = dataclasses.asdict(response)

      # Extract sql from the response
      sql_response = response_dict.get('sql', '').strip().lower()
      LOG.info(sql_response)
      assert scenario["expected_response"]["sql"] in sql_response, "SQL does not contain a SELECT statement"
      check_warning(response_dict, scenario["expected_response"], "warning")
      check_warning(response_dict, scenario["expected_response"], "summary")
      check_warning(response_dict, scenario["expected_response"], "semanticerror")
      check_warning(response_dict, scenario["expected_response"], "sqlerror")
      check_warning(response_dict, scenario["expected_response"], "explain")

    for scenario in edit_scenarios:
      inputJson = {
        "task": "edit",
        "sql": scenario["sql"],
        "input": scenario['input'],
        "dialect": "hive",
        "metadata": {
          "tables": tables_metadata
        }
        }
      task = inputJson["task"]
      input = inputJson["input"]
      sql_query =  inputJson["sql"]
      dialect = inputJson["dialect"]
      metadata = inputJson["metadata"]


      response = perform_sql_task(task, input, sql_query, dialect, metadata)

      # Convert SQLResponse to dictionary
      response_dict = dataclasses.asdict(response)

      # Extract sql from the response
      sql_response = response_dict.get('sql', '').strip().lower()

      check_warning(response_dict, scenario["expected_response"], "warning")
      check_warning(response_dict, scenario["expected_response"], "summary")
      check_warning(response_dict, scenario["expected_response"], "semanticerror")
      check_warning(response_dict, scenario["expected_response"], "sqlerror")
      check_warning(response_dict, scenario["expected_response"], "explain")
      assert scenario["expected_response"]["sql"] in sql_response, "SQL does not contain a SELECT statement"


def check_warning(response, expected_response, keyName):
    print(response, expected_response, keyName)

    if keyName in response and keyName in expected_response:
        if expected_response[keyName] is False:
            assert response[keyName] in [None, False, ""], f"Mismatch in warning: {keyName}"
        else:
            assert response[keyName] not in [None, False, ""], f"Different Than Expected: {keyName}"
    else:
        print(f"{keyName} is not present in either response or expected_response.")