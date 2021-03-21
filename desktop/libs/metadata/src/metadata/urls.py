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

import sys

from metadata import catalog_api as metadata_catalog_api, analytic_db_api, dataeng_api, prometheus_api
from metadata import optimizer_api as metadata_optimizer_api
from metadata import workload_analytics_api as metadata_workload_analytics_api
from metadata import manager_api as metadata_manager_api

if sys.version_info[0] > 2:
  from django.urls import re_path
else:
  from django.conf.urls import url as re_path


# Catalog
urlpatterns = [
  re_path(r'^api/catalog/search_entities/?$', metadata_catalog_api.search_entities, name='catalog_search_entities'),
  re_path(
    r'^api/catalog/search_entities_interactive/?$',
    metadata_catalog_api.search_entities_interactive,
    name='catalog_search_entities_interactive'
  ),
  re_path(r'^api/catalog/find_entity/?$', metadata_catalog_api.find_entity, name='catalog_find_entity'),
  re_path(r'^api/catalog/get_entity/?$', metadata_catalog_api.get_entity, name='catalog_get_entity'),
  re_path(r'^api/catalog/add_tags/?$', metadata_catalog_api.add_tags, name='catalog_add_tags'),
  re_path(r'^api/catalog/delete_tags/?$', metadata_catalog_api.delete_tags, name='catalog_delete_tags'),
  re_path(r'^api/catalog/list_tags/?$', metadata_catalog_api.list_tags, name='catalog_list_tags'),
  re_path(r'^api/catalog/suggest/?$', metadata_catalog_api.suggest, name='catalog_suggest'),
  re_path(r'^api/catalog/update_properties/?$', metadata_catalog_api.update_properties, name='catalog_update_properties'),
  re_path(
    r'^api/catalog/delete_metadata_properties/?$',
    metadata_catalog_api.delete_metadata_properties,
    name='catalog_delete_metadata_properties'
  ),
  re_path(r'^api/catalog/lineage/?$', metadata_catalog_api.get_lineage, name='catalog_get_lineage'),
]
# Navigator API (deprecated, renamed to Catalog)
urlpatterns += [
  re_path(r'^api/navigator/search_entities/?$', metadata_catalog_api.search_entities, name='search_entities'),
  re_path(
    r'^api/navigator/search_entities_interactive/?$',
    metadata_catalog_api.search_entities_interactive,
    name='search_entities_interactive'
  ),
  re_path(r'^api/navigator/find_entity/?$', metadata_catalog_api.find_entity, name='find_entity'),
  re_path(r'^api/navigator/get_entity/?$', metadata_catalog_api.get_entity, name='get_entity'),
  re_path(r'^api/navigator/add_tags/?$', metadata_catalog_api.add_tags, name='add_tags'),
  re_path(r'^api/navigator/delete_tags/?$', metadata_catalog_api.delete_tags, name='delete_tags'),
  re_path(r'^api/navigator/list_tags/?$', metadata_catalog_api.list_tags, name='list_tags'),
  re_path(r'^api/navigator/suggest/?$', metadata_catalog_api.suggest, name='suggest'),
  re_path(r'^api/navigator/update_properties/?$', metadata_catalog_api.update_properties, name='update_properties'),
  re_path(
    r'^api/navigator/delete_metadata_properties/?$', metadata_catalog_api.delete_metadata_properties, name='delete_metadata_properties'
  ),
  re_path(r'^api/navigator/lineage/?$', metadata_catalog_api.get_lineage, name='get_lineage'),
]

# Optimizer API
urlpatterns += [
  re_path(r'^api/optimizer/upload/history/?$', metadata_optimizer_api.upload_history, name='upload_history'),
  re_path(r'^api/optimizer/upload/query/?$', metadata_optimizer_api.upload_query, name='upload_query'),
  re_path(r'^api/optimizer/upload/table_stats/?$', metadata_optimizer_api.upload_table_stats, name='upload_table_stats'),
  re_path(r'^api/optimizer/upload/status/?$', metadata_optimizer_api.upload_status, name='upload_status'),

  #v2
  re_path(r'^api/optimizer/get_tenant/?$', metadata_optimizer_api.get_tenant, name='get_tenant'),

  re_path(r'^api/optimizer/top_databases/?$', metadata_optimizer_api.top_databases, name='top_databases'),
  re_path(r'^api/optimizer/top_tables/?$', metadata_optimizer_api.top_tables, name='top_tables'),
  re_path(r'^api/optimizer/top_columns/?$', metadata_optimizer_api.top_columns, name='top_columns'),
  re_path(r'^api/optimizer/top_joins/?$', metadata_optimizer_api.top_joins, name='top_joins'),
  re_path(r'^api/optimizer/top_filters/?$', metadata_optimizer_api.top_filters, name='top_filters'),
  re_path(r'^api/optimizer/top_aggs/?$', metadata_optimizer_api.top_aggs, name='top_aggs'),

  re_path(r'^api/optimizer/table_details/?$', metadata_optimizer_api.table_details, name='table_details'),

  re_path(r'^api/optimizer/query_risk/?$', metadata_optimizer_api.query_risk, name='query_risk'),
  re_path(r'^api/optimizer/predict/?$', metadata_optimizer_api.predict, name='predict'),
  re_path(r'^api/optimizer/query_compatibility/?$', metadata_optimizer_api.query_compatibility, name='query_compatibility'),
  re_path(r'^api/optimizer/similar_queries/?$', metadata_optimizer_api.similar_queries, name='similar_queries'),
]


# Manager API
urlpatterns += [
  re_path(r'^api/manager/hello/?$', metadata_manager_api.hello, name='manager_hello'),
  re_path(r'^api/manager/get_hosts/?$', metadata_manager_api.get_hosts, name='manager_hosts'),
  re_path(r'^api/manager/update_flume_config/?$', metadata_manager_api.update_flume_config, name='manager_update_flume_config'),
]


# Prometheus API
urlpatterns += [
  re_path(r'^api/prometheus/query?$', prometheus_api.query, name='prometheus_query'),
]


# Altus API
urlpatterns += [
  re_path(r'^api/analytic_db/create_cluster/?$', analytic_db_api.create_cluster, name='create_cluster'),
  re_path(r'^api/analytic_db/update_cluster/?$', analytic_db_api.update_cluster, name='update_cluster'),
]
urlpatterns += [
  re_path(r'^api/dataeng/create_cluster/?$', dataeng_api.create_cluster, name='create_cluster'),
]
urlpatterns += [
  re_path(
    r'^api/workload_analytics/get_operation_execution_details/?$',
    metadata_workload_analytics_api.get_operation_execution_details,
    name='get_operation_execution_details'
  ),
  re_path(r'^api/workload_analytics/get_impala_query/?$', metadata_workload_analytics_api.get_impala_query, name='get_impala_query'),
  re_path(r'^api/workload_analytics/get_environment/?$', metadata_workload_analytics_api.get_environment, name='get_environment'),
]
