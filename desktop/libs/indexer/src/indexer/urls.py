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

from indexer.conf import ENABLE_NEW_INDEXER


urlpatterns = patterns('indexer.views',
  url(r'^install_examples$', 'install_examples', name='install_examples'),

  url(r'^importer/$', 'importer', name='importer'),
  url(r'^importer/prefill/(?P<source_type>[^/]+)/(?P<target_type>[^/]+)/(?P<target_path>[^/]+)?$', 'importer_prefill', name='importer_prefill'),
)

if ENABLE_NEW_INDEXER.get():
  urlpatterns += patterns('indexer.views',
    url(r'^$', 'indexes', name='indexes'),
    url(r'^indexes/$', 'indexes', name='indexes'),
    url(r'^indexes/(?P<index>[^/]+)/?$', 'indexes', name='indexes'),
    url(r'^collections$', 'collections', name='collections'), # Old page
  )
else:
  urlpatterns += patterns('indexer.views',
    url(r'^$', 'collections', name='collections'),
    url(r'^indexes/$', 'indexes', name='indexes'),
  )

# Kafka
urlpatterns += patterns('indexer.views',
    url(r'^topics/$', 'topics', name='topics'),
    url(r'^topics/(?P<index>[^/]+)/?$', 'topics', name='topics'),
)


urlpatterns += patterns('indexer.solr_api',
  # V2
  url(r'^api/aliases/create/$', 'create_alias', name='create_alias'),
  url(r'^api/configs/list/$', 'list_configs', name='list_configs'),
  url(r'^api/index/list/$', 'list_index', name='list_index'),
  url(r'^api/indexes/list/$', 'list_indexes', name='list_indexes'),
  url(r'^api/indexes/create/$', 'create_index', name='create_index'),
  url(r'^api/indexes/sample/$', 'sample_index', name='sample_index'),
  url(r'^api/indexes/config/$', 'config_index', name='config_index'),
  url(r'^api/indexes/delete/$', 'delete_indexes', name='delete_indexes'),
)

urlpatterns += patterns('indexer.api3',
  # Importer
  url(r'^api/indexer/guess_format/$', 'guess_format', name='guess_format'),
  url(r'^api/indexer/guess_field_types/$', 'guess_field_types', name='guess_field_types'),

  url(r'^api/importer/submit', 'importer_submit', name='importer_submit')
)

urlpatterns += patterns('indexer.indexers.rdbms',
  url(r'^api/indexer/indexers/get_db_component/$', 'get_db_component', name='get_db_component'),
  url(r'^api/indexer/indexers/get_drivers/$', 'get_drivers', name='get_drivers'),
  url(r'^api/indexer/indexers/jdbc_db_list/$', 'jdbc_db_list', name='jdbc_db_list')
)


# Deprecated
urlpatterns += patterns('indexer.api',
  url(r'^api/fields/parse/$', 'parse_fields', name='api_parse_fields'),
  url(r'^api/autocomplete/$', 'autocomplete', name='api_autocomplete'),
  url(r'^api/collections/$', 'collections', name='api_collections'),
  url(r'^api/collections/create/$', 'collections_create', name='api_collections_create'),
  url(r'^api/collections/import/$', 'collections_import', name='api_collections_import'),
  url(r'^api/collections/remove/$', 'collections_remove', name='api_collections_remove'),
  url(r'^api/collections/(?P<collection>[^/]+)/fields/$', 'collections_fields', name='api_collections_fields'),
  url(r'^api/collections/(?P<collection>[^/]+)/update/$', 'collections_update', name='api_collections_update'),
  url(r'^api/collections/(?P<collection>[^/]+)/data/$', 'collections_data', name='api_collections_data'),
)