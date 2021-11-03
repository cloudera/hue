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

from indexer import views as indexer_views
from indexer import solr_api as indexer_solr_api
from indexer import api3 as indexer_api3
from indexer.indexers import rdbms as indexer_indexers_rdbms
from indexer import api as indexer_api

from indexer.conf import ENABLE_NEW_INDEXER

if sys.version_info[0] > 2:
  from django.urls import re_path
else:
  from django.conf.urls import url as re_path

urlpatterns = [
  re_path(r'^install_examples$', indexer_views.install_examples, name='install_examples'),

  re_path(r'^importer/?$', indexer_views.importer, name='importer'),
  re_path(
    r'^importer/prefill/(?P<source_type>[^/]+)/(?P<target_type>[^/]+)/(?P<target_path>[^/]+)?$',
    indexer_views.importer_prefill,
    name='importer_prefill'
  ),
]

if ENABLE_NEW_INDEXER.get():
  urlpatterns += [
    re_path(r'^$', indexer_views.indexes, name='indexes'),
    re_path(r'^indexes/?$', indexer_views.indexes, name='indexes'),
    re_path(r'^indexes/(?P<index>[^/]+)/?$', indexer_views.indexes, name='indexes'),
    re_path(r'^collections$', indexer_views.collections, name='collections'), # Old page
  ]
else:
  urlpatterns += [
    re_path(r'^$', indexer_views.collections, name='collections'),
    re_path(r'^indexes/?$', indexer_views.indexes, name='indexes'),
  ]

urlpatterns += [
    re_path(r'^topics/?$', indexer_views.topics, name='topics'),
    re_path(r'^topics/(?P<index>[^/]+)/?$', indexer_views.topics, name='topics'),
]


urlpatterns += [
  # V2
  re_path(r'^api/aliases/create/?$', indexer_solr_api.create_alias, name='create_alias'),
  re_path(r'^api/configs/list/?$', indexer_solr_api.list_configs, name='list_configs'),
  re_path(r'^api/index/list/?$', indexer_solr_api.list_index, name='list_index'),
  re_path(r'^api/indexes/list/?$', indexer_solr_api.list_indexes, name='list_indexes'),
  re_path(r'^api/indexes/create/?$', indexer_solr_api.create_index, name='create_index'),
  re_path(r'^api/indexes/index/?$', indexer_solr_api.index, name='index'),
  re_path(r'^api/indexes/sample/?$', indexer_solr_api.sample_index, name='sample_index'),
  re_path(r'^api/indexes/config/?$', indexer_solr_api.config_index, name='config_index'),
  re_path(r'^api/indexes/delete/?$', indexer_solr_api.delete_indexes, name='delete_indexes'),
]

urlpatterns += [
  # Importer
  re_path(r'^api/indexer/guess_format/?$', indexer_api3.guess_format, name='guess_format'),
  re_path(r'^api/indexer/guess_field_types/?$', indexer_api3.guess_field_types, name='guess_field_types'),
  re_path(r'^api/indexer/index/?$', indexer_api3.index, name='index'),

  re_path(r'^api/importer/submit', indexer_api3.importer_submit, name='importer_submit'),
  re_path(r'^api/importer/save/?$', indexer_api3.save_pipeline, name='save_pipeline'),
  
  re_path(r'^api/indexer/upload_local_file/?$', indexer_api3.upload_local_file, name='upload_local_file'),
  re_path(r'^api/indexer/upload_local_file_drag_and_drop/?$', indexer_api3.upload_local_file_drag_and_drop, name='upload_local_file_drag_and_drop'),
]

urlpatterns += [
  re_path(r'^api/indexer/indexers/get_db_component/?$', indexer_indexers_rdbms.get_db_component, name='get_db_component'),
  re_path(r'^api/indexer/indexers/get_drivers/?$', indexer_indexers_rdbms.get_drivers, name='get_drivers'),
  re_path(r'^api/indexer/indexers/jdbc_db_list/?$', indexer_indexers_rdbms.jdbc_db_list, name='jdbc_db_list')
]


# Deprecated
urlpatterns += [
  re_path(r'^api/fields/parse/?$', indexer_api.parse_fields, name='api_parse_fields'),
  re_path(r'^api/autocomplete/?$', indexer_api.autocomplete, name='api_autocomplete'),
  re_path(r'^api/collections/?$', indexer_api.collections, name='api_collections'),
  re_path(r'^api/collections/create/?$', indexer_api.collections_create, name='api_collections_create'),
  re_path(r'^api/collections/import/?$', indexer_api.collections_import, name='api_collections_import'),
  re_path(r'^api/collections/remove/?$', indexer_api.collections_remove, name='api_collections_remove'),
  re_path(r'^api/collections/(?P<collection>[^/]+)/fields/?$', indexer_api.collections_fields, name='api_collections_fields'),
  re_path(r'^api/collections/(?P<collection>[^/]+)/update/?$', indexer_api.collections_update, name='api_collections_update'),
  re_path(r'^api/collections/(?P<collection>[^/]+)/data/?$', indexer_api.collections_data, name='api_collections_data'),
]
