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

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('search.views',
  url(r'^$', 'index', name='index'),
  url(r'^search$', 'search', name='search'),
  url(r'^save$', 'save', name='save'),
  url(r'^new_search', 'new_search', name='new_search'),
  url(r'^browse/(?P<name>.+)', 'browse', name='browse'),
  url(r'^download$', 'download', name='download'),

  url(r'^admin/collections$', 'admin_collections', name='admin_collections'),

  # Ajax
  # Search
  url(r'^suggest/(?P<collection_id>\w+)/(?P<query>\w+)?$', 'query_suggest', name='query_suggest'),
  url(r'^index/fields/dynamic$', 'index_fields_dynamic', name='index_fields_dynamic'),
  url(r'^template/new_facet$', 'new_facet', name='new_facet'),
  url(r'^get_document$', 'get_document', name='get_document'),
  url(r'^get_range_facet$', 'get_range_facet', name='get_range_facet'),
  url(r'^get_timeline$', 'get_timeline', name='get_timeline'),
  url(r'^get_collection$', 'get_collection', name='get_collection'),
  url(r'^get_collections$', 'get_collections', name='get_collections'),
  url(r'^get_stats$', 'get_stats', name='get_stats'),
  url(r'^get_terms$', 'get_terms', name='get_terms'),

  # Admin
  url(r'^admin/collection_delete$', 'admin_collection_delete', name='admin_collection_delete'),
  url(r'^admin/collection_copy$', 'admin_collection_copy', name='admin_collection_copy'),

  url(r'^install_examples$', 'install_examples', name='install_examples'),
)
