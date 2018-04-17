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

from django.conf.urls import patterns, url


# Navigator API
urlpatterns = patterns('metadata.navigator_api',
  url(r'^api/navigator/search_entities/?$', 'search_entities', name='search_entities'),
  url(r'^api/navigator/search_entities_interactive/?$', 'search_entities_interactive', name='search_entities_interactive'),
  url(r'^api/navigator/find_entity/?$', 'find_entity', name='find_entity'),
  url(r'^api/navigator/get_entity/?$', 'get_entity', name='get_entity'),
  url(r'^api/navigator/add_tags/?$', 'add_tags', name='add_tags'),
  url(r'^api/navigator/delete_tags/?$', 'delete_tags', name='delete_tags'),
  url(r'^api/navigator/list_tags/?$', 'list_tags', name='list_tags'),
  url(r'^api/navigator/suggest/?$', 'suggest', name='suggest'),
  url(r'^api/navigator/update_properties/?$', 'update_properties', name='update_properties'),
  url(r'^api/navigator/delete_metadata_properties/?$', 'delete_metadata_properties', name='delete_metadata_properties'),
  url(r'^api/navigator/lineage/?$', 'get_lineage', name='get_lineage'),
  url(r'^api/navigator/namespace/create/?$', 'create_namespace', name='create_namespace'),
  url(r'^api/navigator/namespace/?$', 'get_namespace', name='get_namespace'),
  url(r'^api/navigator/namespace/property/create/?$', 'create_namespace_property', name='create_namespace_property'),
  url(r'^api/navigator/namespace/property/map/?$', 'map_namespace_property', name='map_namespace_property'),
  url(r'^api/navigator/models/properties/mappings/?$', 'get_model_properties_mapping', name='get_model_properties_mapping'),
)


# Optimizer API
urlpatterns += patterns('metadata.optimizer_api',
  url(r'^api/optimizer/upload/history/?$', 'upload_history', name='upload_history'),
  url(r'^api/optimizer/upload/query/?$', 'upload_query', name='upload_query'),
  url(r'^api/optimizer/upload/table_stats/?$', 'upload_table_stats', name='upload_table_stats'),
  url(r'^api/optimizer/upload/status/?$', 'upload_status', name='upload_status'),

  #v2
  url(r'^api/optimizer/get_tenant/?$', 'get_tenant', name='get_tenant'),

  url(r'^api/optimizer/top_databases/?$', 'top_databases', name='top_databases'),
  url(r'^api/optimizer/top_tables/?$', 'top_tables', name='top_tables'),
  url(r'^api/optimizer/top_columns/?$', 'top_columns', name='top_columns'),
  url(r'^api/optimizer/top_joins/?$', 'top_joins', name='top_joins'),
  url(r'^api/optimizer/top_filters/?$', 'top_filters', name='top_filters'),
  url(r'^api/optimizer/top_aggs/?$', 'top_aggs', name='top_aggs'),

  url(r'^api/optimizer/table_details/?$', 'table_details', name='table_details'),

  url(r'^api/optimizer/query_risk/?$', 'query_risk', name='query_risk'),
  url(r'^api/optimizer/query_compatibility/?$', 'query_compatibility', name='query_compatibility'),
  url(r'^api/optimizer/similar_queries/?$', 'similar_queries', name='similar_queries'),
)


# Manager API
urlpatterns += patterns('metadata.manager_api',
  url(r'^api/manager/hello/?$', 'hello', name='hello'),
)



# Workload Analytics API
urlpatterns += patterns('metadata.workload_analytics_api',
  url(r'^api/workload_analytics/get_operation_execution_details/?$', 'get_operation_execution_details', name='get_operation_execution_details'),
)
