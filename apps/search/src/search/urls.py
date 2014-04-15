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
  url(r'^download/(?P<format>(csv|xls))$', 'download', name='download'),

  url(r'^dashboard$', 'dashboard', name='dashboard'),

  # All admin is deprecated
  url(r'^admin/collections$', 'admin_collections', name='admin_collections'),
  url(r'^admin/collections_import$', 'admin_collections_import', name='admin_collections_import'),

  url(r'^admin/collection/(?P<collection_id>\d+)$', 'admin_collection_template', name='admin_collection'),
  url(r'^admin/collection/(?P<collection_id>\d+)/properties$', 'admin_collection_properties', name='admin_collection_properties'),
  url(r'^admin/collection/(?P<collection_id>\d+)/template$', 'admin_collection_template', name='admin_collection_template'),
  url(r'^admin/collection/(?P<collection_id>\d+)/facets$', 'admin_collection_facets', name='admin_collection_facets'),
  url(r'^admin/collection/(?P<collection_id>\d+)/highlighting$', 'admin_collection_highlighting', name='admin_collection_highlighting'),
  url(r'^admin/collection/(?P<collection_id>\d+)/sorting$', 'admin_collection_sorting', name='admin_collection_sorting'),

  # Ajax
  url(r'^suggest/(?P<collection_id>\w+)/(?P<query>\w+)?$', 'query_suggest', name='query_suggest'),
  url(r'^index/(?P<collection_id>\w+)/fields/dynamic$', 'index_fields_dynamic', name='index_fields_dynamic'),
  url(r'^admin/collection/(?P<collection_id>\w+)/schema$', 'admin_collection_schema', name='admin_collection_schema'),
  url(r'^admin/collection/(?P<collection_id>\w+)/solr_properties$', 'admin_collection_solr_properties', name='admin_collection_solr_properties'),
  url(r'^admin/collection_delete$', 'admin_collection_delete', name='admin_collection_delete'),
  url(r'^admin/collection_copy$', 'admin_collection_copy', name='admin_collection_copy'),
  
  
  
  url(r'^install_examples$', 'install_examples', name='install_examples'),
)
