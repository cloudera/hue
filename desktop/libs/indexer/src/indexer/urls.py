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

urlpatterns = patterns('indexer.views',
  url(r'^$', 'collections', name='collections'),
  url(r'^install_examples$', 'install_examples', name='install_examples'),
  
  # V2
  url(r'^indexes/$', 'indexes', name='indexes'),

  # V3
  url(r'^indexer/$', 'indexer', name='indexer'),
  url(r'^importer/$', 'importer', name='importer')
)

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


urlpatterns += patterns('indexer.api2',
  # V2
  url(r'^api/aliases/create_or_edit/$', 'create_or_edit_alias', name='create_or_edit_alias'),
  url(r'^api/indexes/create/$', 'create_index', name='create_index'),
  url(r'^api/indexes/delete/$', 'delete_indexes', name='delete_indexes'),
  url(r'^api/indexes/create_wizard_get_sample/$', 'create_wizard_get_sample', name='create_wizard_get_sample'),
  url(r'^api/indexes/create_wizard_create/$', 'create_wizard_create', name='create_wizard_create'),
  url(r'^api/indexes/(?P<index>\w+)/schema/$', 'design_schema', name='design_schema')
)

urlpatterns += patterns('indexer.api3',
  # V3
  url(r'^api/indexer/guess_format/$', 'guess_format', name='guess_format'),
  url(r'^api/indexer/index_file/$', 'index_file', name='index_file'),
  url(r'^api/indexer/guess_field_types/$', 'guess_field_types', name='guess_field_types'),
)