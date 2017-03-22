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

urlpatterns = patterns('dashboard.views',
  url(r'^$', 'index', name='index'),
  url(r'^m$', 'index_m', name='index_m'),
  url(r'^save$', 'save', name='save'),
  url(r'^new_search', 'new_search', name='new_search'),
  url(r'^browse/(?P<name>.+)', 'browse', name='browse'),
  url(r'^browse_m/(?P<name>.+)', 'browse_m', name='browse_m'),

  # Admin
  url(r'^admin/collections$', 'admin_collections', name='admin_collections'),
  url(r'^admin/collection_delete$', 'admin_collection_delete', name='admin_collection_delete'),
  url(r'^admin/collection_copy$', 'admin_collection_copy', name='admin_collection_copy'),
)


urlpatterns += patterns('dashboard.api',
  url(r'^search$', 'search', name='search'),
  url(r'^suggest/$', 'query_suggest', name='query_suggest'),
  url(r'^index/fields/dynamic$', 'index_fields_dynamic', name='index_fields_dynamic'),
  url(r'^index/fields/nested_documents', 'nested_documents', name='nested_documents'),
  url(r'^template/new_facet$', 'new_facet', name='new_facet'),
  url(r'^get_document$', 'get_document', name='get_document'),
  url(r'^update_document$', 'update_document', name='update_document'),
  url(r'^get_range_facet$', 'get_range_facet', name='get_range_facet'),
  url(r'^download$', 'download', name='download'),
  url(r'^get_timeline$', 'get_timeline', name='get_timeline'),
  url(r'^get_collection$', 'get_collection', name='get_collection'),
  url(r'^get_collections$', 'get_collections', name='get_collections'),
  url(r'^get_stats$', 'get_stats', name='get_stats'),
  url(r'^get_terms$', 'get_terms', name='get_terms'),
)
