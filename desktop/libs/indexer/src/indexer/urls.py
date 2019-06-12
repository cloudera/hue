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

from django.conf.urls import url
from indexer import views as indexer_views
from indexer import solr_api as indexer_solr_api 
from indexer import api3 as indexer_api3
from indexer.indexers import rdbms as indexer_indexers_rdbms
from indexer import api as indexer_api

from indexer.conf import ENABLE_NEW_INDEXER

urlpatterns = [
  url(r'^install_examples$', indexer_views.install_examples, name='install_examples'),

  url(r'^importer/?$', indexer_views.importer, name='importer'),
  url(r'^importer/prefill/(?P<source_type>[^/]+)/(?P<target_type>[^/]+)/(?P<target_path>[^/]+)?$', indexer_views.importer_prefill, name='importer_prefill'),
]

if ENABLE_NEW_INDEXER.get():
  urlpatterns += [
    url(r'^$', indexer_views.indexes, name='indexes'),
    url(r'^indexes/?$', indexer_views.indexes, name='indexes'),
    url(r'^indexes/(?P<index>[^/]+)/?$', indexer_views.indexes, name='indexes'),
    url(r'^collections$', indexer_views.collections, name='collections'), # Old page
  ]
else:
  urlpatterns += [
    url(r'^$', indexer_views.collections, name='collections'),
    url(r'^indexes/?$', indexer_views.indexes, name='indexes'),
  ]

urlpatterns += [
    url(r'^topics/?$', indexer_views.topics, name='topics'),
    url(r'^topics/(?P<index>[^/]+)/?$', indexer_views.topics, name='topics'),
]


urlpatterns += [
  # V2
  url(r'^api/aliases/create/?$', indexer_solr_api.create_alias, name='create_alias'),
  url(r'^api/configs/list/?$', indexer_solr_api.list_configs, name='list_configs'),
  url(r'^api/index/list/?$', indexer_solr_api.list_index, name='list_index'),
  url(r'^api/indexes/list/?$', indexer_solr_api.list_indexes, name='list_indexes'),
  url(r'^api/indexes/create/?$', indexer_solr_api.create_index, name='create_index'),
  url(r'^api/indexes/index/?$', indexer_solr_api.index, name='index'),
  url(r'^api/indexes/sample/?$', indexer_solr_api.sample_index, name='sample_index'),
  url(r'^api/indexes/config/?$', indexer_solr_api.config_index, name='config_index'),
  url(r'^api/indexes/delete/?$', indexer_solr_api.delete_indexes, name='delete_indexes'),
]

urlpatterns += [
  # Importer
  url(r'^api/indexer/guess_format/?$', indexer_api3.guess_format, name='guess_format'),
  url(r'^api/indexer/guess_field_types/?$', indexer_api3.guess_field_types, name='guess_field_types'),

  url(r'^api/importer/submit', indexer_api3.importer_submit, name='importer_submit'),
  url(r'^api/importer/save/?$', indexer_api3.save_pipeline, name='save_pipeline'),
]

urlpatterns += [
  url(r'^api/indexer/indexers/get_db_component/?$', indexer_indexers_rdbms.get_db_component, name='get_db_component'),
  url(r'^api/indexer/indexers/get_drivers/?$', indexer_indexers_rdbms.get_drivers, name='get_drivers'),
  url(r'^api/indexer/indexers/jdbc_db_list/?$', indexer_indexers_rdbms.jdbc_db_list, name='jdbc_db_list')
]


# Deprecated
urlpatterns += [
  url(r'^api/fields/parse/?$', indexer_api.parse_fields, name='api_parse_fields'),
  url(r'^api/autocomplete/?$', indexer_api.autocomplete, name='api_autocomplete'),
  url(r'^api/collections/?$', indexer_api.collections, name='api_collections'),
  url(r'^api/collections/create/?$', indexer_api.collections_create, name='api_collections_create'),
  url(r'^api/collections/import/?$', indexer_api.collections_import, name='api_collections_import'),
  url(r'^api/collections/remove/?$', indexer_api.collections_remove, name='api_collections_remove'),
  url(r'^api/collections/(?P<collection>[^/]+)/fields/?$', indexer_api.collections_fields, name='api_collections_fields'),
  url(r'^api/collections/(?P<collection>[^/]+)/update/?$', indexer_api.collections_update, name='api_collections_update'),
  url(r'^api/collections/(?P<collection>[^/]+)/data/?$', indexer_api.collections_data, name='api_collections_data'),
]
