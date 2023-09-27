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
    "name": "catalog_sales",
    "columns": [
      {
        "name": "cs_sold_date_sk",
        "type": "bigint",
        "comment": "",
        "index": 0
      },
      {
        "name": "cs_sold_time_sk",
        "type": "bigint",
        "comment": "",
        "index": 1
      },
      {
        "name": "cs_ship_date_sk",
        "type": "bigint",
        "comment": "",
        "index": 2
      },
      {
        "name": "cs_bill_customer_sk",
        "type": "bigint",
        "comment": "",
        "index": 3
      },
      {
        "name": "cs_bill_cdemo_sk",
        "type": "bigint",
        "comment": "",
        "index": 4
      },
      {
        "name": "cs_bill_hdemo_sk",
        "type": "bigint",
        "comment": "",
        "index": 5
      },
      {
        "name": "cs_bill_addr_sk",
        "type": "bigint",
        "comment": "",
        "index": 6
      },
      {
        "name": "cs_ship_customer_sk",
        "type": "bigint",
        "comment": "",
        "index": 7
      },
      {
        "name": "cs_ship_cdemo_sk",
        "type": "bigint",
        "comment": "",
        "index": 8
      },
      {
        "name": "cs_ship_hdemo_sk",
        "type": "bigint",
        "comment": "",
        "index": 9
      },
      {
        "name": "cs_ship_addr_sk",
        "type": "bigint",
        "comment": "",
        "index": 10
      },
      {
        "name": "cs_call_center_sk",
        "type": "bigint",
        "comment": "",
        "index": 11
      },
      {
        "name": "cs_catalog_page_sk",
        "type": "bigint",
        "comment": "",
        "index": 12
      },
      {
        "name": "cs_ship_mode_sk",
        "type": "bigint",
        "comment": "",
        "index": 13
      },
      {
        "name": "cs_warehouse_sk",
        "type": "bigint",
        "comment": "",
        "index": 14
      },
      {
        "name": "cs_item_sk",
        "type": "bigint",
        "comment": "",
        "index": 15
      },
      {
        "name": "cs_promo_sk",
        "type": "bigint",
        "comment": "",
        "index": 16
      },
      {
        "name": "cs_order_number",
        "type": "bigint",
        "comment": "",
        "index": 17
      },
      {
        "name": "cs_quantity",
        "type": "int",
        "comment": "",
        "index": 18
      },
      {
        "name": "cs_wholesale_cost",
        "type": "decimal(7,2)",
        "comment": "",
        "index": 19
      },
      {
        "name": "cs_list_price",
        "type": "decimal(7,2)",
        "comment": "",
        "index": 20
      },
      {
        "name": "cs_sales_price",
        "type": "decimal(7,2)",
        "comment": "",
        "index": 21
      },
      {
        "name": "cs_ext_discount_amt",
        "type": "decimal(7,2)",
        "comment": "",
        "index": 22
      },
      {
        "name": "cs_ext_sales_price",
        "type": "decimal(7,2)",
        "comment": "",
        "index": 23
      },
      {
        "name": "cs_ext_wholesale_cost",
        "type": "decimal(7,2)",
        "comment": "",
        "index": 24
      },
      {
        "name": "cs_ext_list_price",
        "type": "decimal(7,2)",
        "comment": "",
        "index": 25
      },
      {
        "name": "cs_ext_tax",
        "type": "decimal(7,2)",
        "comment": "",
        "index": 26
      },
      {
        "name": "cs_coupon_amt",
        "type": "decimal(7,2)",
        "comment": "",
        "index": 27
      },
      {
        "name": "cs_ext_ship_cost",
        "type": "decimal(7,2)",
        "comment": "",
        "index": 28
      },
      {
        "name": "cs_net_paid",
        "type": "decimal(7,2)",
        "comment": "",
        "index": 29
      },
      {
        "name": "cs_net_paid_inc_tax",
        "type": "decimal(7,2)",
        "comment": "",
        "index": 30
      },
      {
        "name": "cs_net_paid_inc_ship",
        "type": "decimal(7,2)",
        "comment": "",
        "index": 31
      },
      {
        "name": "cs_net_paid_inc_ship_tax",
        "type": "decimal(7,2)",
        "comment": "",
        "index": 32
      },
      {
        "name": "cs_net_profit",
        "type": "decimal(7,2)",
        "comment": "",
        "index": 33
      }
    ]
  },
  {
    "name": "customer_address",
    "columns": [
      {
        "name": "ca_address_sk",
        "type": "bigint",
        "comment": "",
        "index": 0
      },
      {
        "name": "ca_address_id",
        "type": "char(16)",
        "comment": "",
        "index": 1
      },
      {
        "name": "ca_street_number",
        "type": "char(10)",
        "comment": "",
        "index": 2
      },
      {
        "name": "ca_street_name",
        "type": "varchar(60)",
        "comment": "",
        "index": 3
      },
      {
        "name": "ca_street_type",
        "type": "char(15)",
        "comment": "",
        "index": 4
      },
      {
        "name": "ca_suite_number",
        "type": "char(10)",
        "comment": "",
        "index": 5
      },
      {
        "name": "ca_city",
        "type": "varchar(60)",
        "comment": "",
        "index": 6
      },
      {
        "name": "ca_county",
        "type": "varchar(30)",
        "comment": "",
        "index": 7
      },
      {
        "name": "ca_state",
        "type": "char(2)",
        "comment": "",
        "index": 8
      },
      {
        "name": "ca_zip",
        "type": "char(10)",
        "comment": "",
        "index": 9
      },
      {
        "name": "ca_country",
        "type": "varchar(20)",
        "comment": "",
        "index": 10
      },
      {
        "name": "ca_gmt_offset",
        "type": "decimal(5,2)",
        "comment": "",
        "index": 11
      },
      {
        "name": "ca_location_type",
        "type": "char(20)",
        "comment": "",
        "index": 12
      }
    ]
  },
  {
    "name": "income_band",
    "columns": [
      {
        "name": "ib_income_band_sk",
        "type": "bigint",
        "comment": "",
        "index": 0
      },
      {
        "name": "ib_lower_bound",
        "type": "int",
        "comment": "",
        "index": 1
      },
      {
        "name": "ib_upper_bound",
        "type": "int",
        "comment": "",
        "index": 2
      }
    ]
  },
  {
    "name": "reason",
    "columns": [
      {
        "name": "r_reason_sk",
        "type": "bigint",
        "comment": "",
        "index": 0
      },
      {
        "name": "r_reason_id",
        "type": "char(16)",
        "comment": "",
        "index": 1
      },
      {
        "name": "r_reason_desc",
        "type": "char(100)",
        "comment": "",
        "index": 2
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
  {
    "name": "promotion",
    "columns": [
      {
        "name": "p_promo_sk",
        "type": "bigint",
        "comment": "",
        "index": 0
      },
      {
        "name": "p_promo_id",
        "type": "char(16)",
        "comment": "",
        "index": 1
      },
      {
        "name": "p_start_date_sk",
        "type": "bigint",
        "comment": "",
        "index": 2
      },
      {
        "name": "p_end_date_sk",
        "type": "bigint",
        "comment": "",
        "index": 3
      },
      {
        "name": "p_item_sk",
        "type": "bigint",
        "comment": "",
        "index": 4
      },
      {
        "name": "p_cost",
        "type": "decimal(15,2)",
        "comment": "",
        "index": 5
      },
      {
        "name": "p_response_target",
        "type": "int",
        "comment": "",
        "index": 6
      },
      {
        "name": "p_promo_name",
        "type": "char(50)",
        "comment": "",
        "index": 7
      },
      {
        "name": "p_channel_dmail",
        "type": "char(1)",
        "comment": "",
        "index": 8
      },
      {
        "name": "p_channel_email",
        "type": "char(1)",
        "comment": "",
        "index": 9
      },
      {
        "name": "p_channel_catalog",
        "type": "char(1)",
        "comment": "",
        "index": 10
      },
      {
        "name": "p_channel_tv",
        "type": "char(1)",
        "comment": "",
        "index": 11
      },
      {
        "name": "p_channel_radio",
        "type": "char(1)",
        "comment": "",
        "index": 12
      },
      {
        "name": "p_channel_press",
        "type": "char(1)",
        "comment": "",
        "index": 13
      },
      {
        "name": "p_channel_event",
        "type": "char(1)",
        "comment": "",
        "index": 14
      },
      {
        "name": "p_channel_demo",
        "type": "char(1)",
        "comment": "",
        "index": 15
      },
      {
        "name": "p_channel_details",
        "type": "varchar(100)",
        "comment": "",
        "index": 16
      },
      {
        "name": "p_purpose",
        "type": "char(15)",
        "comment": "",
        "index": 17
      },
      {
        "name": "p_discount_active",
        "type": "char(1)",
        "comment": "",
        "index": 18
      }
    ]
  }
]

generate_scenarios = [
    # {
    #     "scenario": "Generate",
    #     "sql": "",
    #     "ddl":  "CREATE TABLE store (s_store_sk bigint, s_store_id char(16), s_rec_start_date date, s_rec_end_date date, s_closed_date_sk bigint, s_store_name varchar(50), s_number_employees int, s_floor_space int, s_hours char(20), s_manager varchar(40), s_market_id int, s_geography_class varchar(100), s_market_desc varchar(100), s_market_manager varchar(40), s_division_id int, s_division_name varchar(50), s_company_id int, s_company_name varchar(50), s_street_number varchar(10), s_street_name varchar(60), s_street_type char(15), s_suite_number char(10), s_city varchar(60), s_county varchar(30), s_state char(2), s_zip char(10), s_country varchar(20), s_gmt_offset decimal(5,2), s_tax_percentage decimal(5,2));\n\nCREATE TABLE store_sales (ss_sold_date_sk bigint, ss_sold_time_sk bigint, ss_item_sk bigint, ss_customer_sk bigint, ss_cdemo_sk bigint, ss_hdemo_sk bigint, ss_addr_sk bigint, ss_store_sk bigint, ss_promo_sk bigint, ss_ticket_number bigint, ss_quantity int, ss_wholesale_cost decimal(7,2), ss_list_price decimal(7,2), ss_sales_price decimal(7,2), ss_ext_discount_amt decimal(7,2), ss_ext_sales_price decimal(7,2), ss_ext_wholesale_cost decimal(7,2), ss_ext_list_price decimal(7,2), ss_ext_tax decimal(7,2), ss_coupon_amt decimal(7,2), ss_net_paid decimal(7,2), ss_net_paid_inc_tax decimal(7,2), ss_net_profit decimal(7,2));\n\nCREATE TABLE item (i_item_sk bigint, i_item_id char(16), i_rec_start_date date, i_rec_end_date date, i_item_desc varchar(200), i_current_price decimal(7,2), i_wholesale_cost decimal(7,2), i_brand_id int, i_brand char(50), i_class_id int, i_class char(50), i_category_id int, i_category char(50), i_manufact_id int, i_manufact char(50), i_size char(20), i_formulation char(20), i_color char(20), i_units char(10), i_container char(10), i_manager_id int, i_product_name char(50));\n\nCREATE TABLE promotion (p_promo_sk bigint, p_promo_id char(16), p_start_date_sk bigint, p_end_date_sk bigint, p_item_sk bigint, p_cost decimal(15,2), p_response_target int, p_promo_name char(50), p_channel_dmail char(1), p_channel_email char(1), p_channel_catalog char(1), p_channel_tv char(1), p_channel_radio char(1), p_channel_press char(1), p_channel_event char(1), p_channel_demo char(1), p_channel_details varchar(100), p_purpose char(15), p_discount_active char(1));\n\nCREATE TABLE catalog_sales (cs_sold_date_sk bigint, cs_sold_time_sk bigint, cs_ship_date_sk bigint, cs_bill_customer_sk bigint, cs_bill_cdemo_sk bigint, cs_bill_hdemo_sk bigint, cs_bill_addr_sk bigint, cs_ship_customer_sk bigint, cs_ship_cdemo_sk bigint, cs_ship_hdemo_sk bigint, cs_ship_addr_sk bigint, cs_call_center_sk bigint, cs_catalog_page_sk bigint, cs_ship_mode_sk bigint, cs_warehouse_sk bigint, cs_item_sk bigint, cs_promo_sk bigint, cs_order_number bigint, cs_quantity int, cs_wholesale_cost decimal(7,2), cs_list_price decimal(7,2), cs_sales_price decimal(7,2), cs_ext_discount_amt decimal(7,2), cs_ext_sales_price decimal(7,2), cs_ext_wholesale_cost decimal(7,2), cs_ext_list_price decimal(7,2), cs_ext_tax decimal(7,2), cs_coupon_amt decimal(7,2), cs_ext_ship_cost decimal(7,2), cs_net_paid decimal(7,2), cs_net_paid_inc_tax decimal(7,2), cs_net_paid_inc_ship decimal(7,2), cs_net_paid_inc_ship_tax decimal(7,2), cs_net_profit decimal(7,2));\n\nCREATE TABLE store_returns (sr_returned_date_sk bigint, sr_return_time_sk bigint, sr_item_sk bigint, sr_customer_sk bigint, sr_cdemo_sk bigint, sr_hdemo_sk bigint, sr_addr_sk bigint, sr_store_sk bigint, sr_reason_sk bigint, sr_ticket_number bigint, sr_return_quantity int, sr_return_amt decimal(7,2), sr_return_tax decimal(7,2), sr_return_amt_inc_tax decimal(7,2), sr_fee decimal(7,2), sr_return_ship_cost decimal(7,2), sr_refunded_cash decimal(7,2), sr_reversed_charge decimal(7,2), sr_store_credit decimal(7,2), sr_net_loss decimal(7,2));\n\nCREATE TABLE time_dim (t_time_sk bigint, t_time_id char(16), t_time int, t_hour int, t_minute int, t_second int, t_am_pm char(2), t_shift char(20), t_sub_shift char(20), t_meal_time char(20));\n\nCREATE TABLE web_sales (ws_sold_date_sk bigint, ws_sold_time_sk bigint, ws_ship_date_sk bigint, ws_item_sk bigint, ws_bill_customer_sk bigint, ws_bill_cdemo_sk bigint, ws_bill_hdemo_sk bigint, ws_bill_addr_sk bigint, ws_ship_customer_sk bigint, ws_ship_cdemo_sk bigint, ws_ship_hdemo_sk bigint, ws_ship_addr_sk bigint, ws_web_page_sk bigint, ws_web_site_sk bigint, ws_ship_mode_sk bigint, ws_warehouse_sk bigint, ws_promo_sk bigint, ws_order_number bigint, ws_quantity int, ws_wholesale_cost decimal(7,2), ws_list_price decimal(7,2), ws_sales_price decimal(7,2), ws_ext_discount_amt decimal(7,2), ws_ext_sales_price decimal(7,2), ws_ext_wholesale_cost decimal(7,2), ws_ext_list_price decimal(7,2), ws_ext_tax decimal(7,2), ws_coupon_amt decimal(7,2), ws_ext_ship_cost decimal(7,2), ws_net_paid decimal(7,2), ws_net_paid_inc_tax decimal(7,2), ws_net_paid_inc_ship decimal(7,2), ws_net_paid_inc_ship_tax decimal(7,2), ws_net_profit decimal(7,2));\n\nCREATE TABLE warehouse (w_warehouse_sk bigint, w_warehouse_id char(16), w_warehouse_name varchar(20), w_warehouse_sq_ft int, w_street_number char(10), w_street_name varchar(60), w_street_type char(15), w_suite_number char(10), w_city varchar(60), w_county varchar(30), w_state char(2), w_zip char(10), w_country varchar(20), w_gmt_offset decimal(5,2));",
    #     "input": "get store name, store id, manager, zipcode,total sales of each store and sort by total sales in ascending order.",
    #     "expected_response": {
    #        "sql": "select",
    #        "warning": False,
    #        "sqlError": False,
    #        "summary": False
    #     }
    # }
]


edit_scenarios = [
    {
        "scenario": "Edit Verify",
        "ddl":  "CREATE TABLE store_sales (ss_sold_date_sk bigint, ss_sold_time_sk bigint, ss_item_sk bigint, ss_customer_sk bigint, ss_cdemo_sk bigint, ss_hdemo_sk bigint, ss_addr_sk bigint, ss_store_sk bigint, ss_promo_sk bigint, ss_ticket_number bigint, ss_quantity int, ss_wholesale_cost decimal(7,2), ss_list_price decimal(7,2), ss_sales_price decimal(7,2), ss_ext_discount_amt decimal(7,2), ss_ext_sales_price decimal(7,2), ss_ext_wholesale_cost decimal(7,2), ss_ext_list_price decimal(7,2), ss_ext_tax decimal(7,2), ss_coupon_amt decimal(7,2), ss_net_paid decimal(7,2), ss_net_paid_inc_tax decimal(7,2), ss_net_profit decimal(7,2));\n\nCREATE TABLE customer (c_customer_sk bigint, c_customer_id char(16), c_current_cdemo_sk bigint, c_current_hdemo_sk bigint, c_current_addr_sk bigint, c_first_shipto_date_sk bigint, c_first_sales_date_sk bigint, c_salutation char(10), c_first_name char(20), c_last_name char(30), c_preferred_cust_flag char(1), c_birth_day int, c_birth_month int, c_birth_year int, c_birth_country varchar(20), c_login char(13), c_email_address char(50), c_last_review_date_sk bigint);\n\nCREATE TABLE catalog_sales (cs_sold_date_sk bigint, cs_sold_time_sk bigint, cs_ship_date_sk bigint, cs_bill_customer_sk bigint, cs_bill_cdemo_sk bigint, cs_bill_hdemo_sk bigint, cs_bill_addr_sk bigint, cs_ship_customer_sk bigint, cs_ship_cdemo_sk bigint, cs_ship_hdemo_sk bigint, cs_ship_addr_sk bigint, cs_call_center_sk bigint, cs_catalog_page_sk bigint, cs_ship_mode_sk bigint, cs_warehouse_sk bigint, cs_item_sk bigint, cs_promo_sk bigint, cs_order_number bigint, cs_quantity int, cs_wholesale_cost decimal(7,2), cs_list_price decimal(7,2), cs_sales_price decimal(7,2), cs_ext_discount_amt decimal(7,2), cs_ext_sales_price decimal(7,2), cs_ext_wholesale_cost decimal(7,2), cs_ext_list_price decimal(7,2), cs_ext_tax decimal(7,2), cs_coupon_amt decimal(7,2), cs_ext_ship_cost decimal(7,2), cs_net_paid decimal(7,2), cs_net_paid_inc_tax decimal(7,2), cs_net_paid_inc_ship decimal(7,2), cs_net_paid_inc_ship_tax decimal(7,2), cs_net_profit decimal(7,2));\n\nCREATE TABLE item (i_item_sk bigint, i_item_id char(16), i_rec_start_date date, i_rec_end_date date, i_item_desc varchar(200), i_current_price decimal(7,2), i_wholesale_cost decimal(7,2), i_brand_id int, i_brand char(50), i_class_id int, i_class char(50), i_category_id int, i_category char(50), i_manufact_id int, i_manufact char(50), i_size char(20), i_formulation char(20), i_color char(20), i_units char(10), i_container char(10), i_manager_id int, i_product_name char(50));\n\nCREATE TABLE store (s_store_sk bigint, s_store_id char(16), s_rec_start_date date, s_rec_end_date date, s_closed_date_sk bigint, s_store_name varchar(50), s_number_employees int, s_floor_space int, s_hours char(20), s_manager varchar(40), s_market_id int, s_geography_class varchar(100), s_market_desc varchar(100), s_market_manager varchar(40), s_division_id int, s_division_name varchar(50), s_company_id int, s_company_name varchar(50), s_street_number varchar(10), s_street_name varchar(60), s_street_type char(15), s_suite_number char(10), s_city varchar(60), s_county varchar(30), s_state char(2), s_zip char(10), s_country varchar(20), s_gmt_offset decimal(5,2), s_tax_percentage decimal(5,2));\n\nCREATE TABLE web_sales (ws_sold_date_sk bigint, ws_sold_time_sk bigint, ws_ship_date_sk bigint, ws_item_sk bigint, ws_bill_customer_sk bigint, ws_bill_cdemo_sk bigint, ws_bill_hdemo_sk bigint, ws_bill_addr_sk bigint, ws_ship_customer_sk bigint, ws_ship_cdemo_sk bigint, ws_ship_hdemo_sk bigint, ws_ship_addr_sk bigint, ws_web_page_sk bigint, ws_web_site_sk bigint, ws_ship_mode_sk bigint, ws_warehouse_sk bigint, ws_promo_sk bigint, ws_order_number bigint, ws_quantity int, ws_wholesale_cost decimal(7,2), ws_list_price decimal(7,2), ws_sales_price decimal(7,2), ws_ext_discount_amt decimal(7,2), ws_ext_sales_price decimal(7,2), ws_ext_wholesale_cost decimal(7,2), ws_ext_list_price decimal(7,2), ws_ext_tax decimal(7,2), ws_coupon_amt decimal(7,2), ws_ext_ship_cost decimal(7,2), ws_net_paid decimal(7,2), ws_net_paid_inc_tax decimal(7,2), ws_net_paid_inc_ship decimal(7,2), ws_net_paid_inc_ship_tax decimal(7,2), ws_net_profit decimal(7,2));\n\nCREATE TABLE warehouse (w_warehouse_sk bigint, w_warehouse_id char(16), w_warehouse_name varchar(20), w_warehouse_sq_ft int, w_street_number char(10), w_street_name varchar(60), w_street_type char(15), w_suite_number char(10), w_city varchar(60), w_county varchar(30), w_state char(2), w_zip char(10), w_country varchar(20), w_gmt_offset decimal(5,2));\n\nCREATE TABLE household_demographics (hd_demo_sk bigint, hd_income_band_sk bigint, hd_buy_potential char(15), hd_dep_count int, hd_vehicle_count int);\n\nCREATE TABLE customer_demographics (cd_demo_sk bigint, cd_gender char(1), cd_marital_status char(1), cd_education_status char(20), cd_purchase_estimate int, cd_credit_rating char(10), cd_dep_count int, cd_dep_employed_count int, cd_dep_college_count int);\n\nCREATE TABLE inventory (inv_date_sk bigint, inv_item_sk bigint, inv_warehouse_sk bigint, inv_quantity_on_hand int);",
        "input": "add sales per employee and sort by sales per employee where sales per employee is total sales by number of employees",
        "sql": "/* NQL: get store name, store id, manager, zipcode,total sales of each store and sort by \ntotal sales in ascending order. */\nSELECT\n  s.s_store_name,\n  s.s_store_id,\n  s.s_manager,\n  s.s_zip,\n  SUM(ss.ss_ext_sales_price) AS total_sales\nFROM\n  store s\n  JOIN store_sales ss ON s.s_store_sk = ss.ss_store_sk\nGROUP BY\n  s.s_store_name,\n  s.s_store_id,\n  s.s_manager,\n  s.s_zip\nORDER BY\n  total_sales ASC;",
        "expected_response": {
           "sql": "select",
           "warning": False,
           "sqlError": False,
           "summary": False
        }
    },
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
          "tables": tables_metadata,
          "ddl": scenario["ddl"]
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
      LOG.info(response_dict)
      # Assert the SQL contains a SELECT statement
      assert scenario["expected_response"]["sql"] in sql_response, "SQL does not contain a SELECT statement"


    for scenario in edit_scenarios:
      inputJson = {
        "task": "edit",
        "sql": scenario["sql"],
        "input": scenario['input'],
        "dialect": "hive",
        "metadata": {
          "tables": tables_metadata,
          "ddl": scenario["ddl"]
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

      assert response_dict.get("sqlerror") not in [None, False, ""], "SQL Error Should be present"
      assert response_dict.get("warning") not in [None, False, ""], "Mismatch in warning."
      assert scenario["expected_response"]["sql"] in sql_response, "SQL does not contain a SELECT statement"