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

from dashboard import views as dashboard_views
from dashboard import api as dashboard_api

if sys.version_info[0] > 2:
  from django.urls import re_path
else:
  from django.conf.urls import url as re_path

urlpatterns = [
  re_path(r'^$', dashboard_views.index, name='index'),
  re_path(r'^m$', dashboard_views.index_m, name='index_m'),
  re_path(r'^save$', dashboard_views.save, name='save'),
  re_path(r'^new_search', dashboard_views.new_search, name='new_search'),
  re_path(r'^browse/(?P<name>[^/]+)/?', dashboard_views.browse, name='browse'),
  re_path(r'^browse_m/(?P<name>[^/]+)/?', dashboard_views.browse_m, name='browse_m'),

  # Admin
  re_path(r'^admin/collections$', dashboard_views.admin_collections, name='admin_collections'),
  re_path(r'^admin/collection_delete$', dashboard_views.admin_collection_delete, name='admin_collection_delete'),
  re_path(r'^admin/collection_copy$', dashboard_views.admin_collection_copy, name='admin_collection_copy'),
]


urlpatterns += [
  re_path(r'^search$', dashboard_api.search, name='search'),
  re_path(r'^suggest/?$', dashboard_api.query_suggest, name='query_suggest'),
  re_path(r'^index/fields/dynamic$', dashboard_api.index_fields_dynamic, name='index_fields_dynamic'),
  re_path(r'^index/fields/nested_documents', dashboard_api.nested_documents, name='nested_documents'),
  re_path(r'^template/new_facet$', dashboard_api.new_facet, name='new_facet'),
  re_path(r'^get_document$', dashboard_api.get_document, name='get_document'),
  re_path(r'^update_document$', dashboard_api.update_document, name='update_document'),
  re_path(r'^get_range_facet$', dashboard_api.get_range_facet, name='get_range_facet'),
  re_path(r'^download$', dashboard_api.download, name='download'),
  re_path(r'^get_timeline$', dashboard_api.get_timeline, name='get_timeline'),
  re_path(r'^get_collection$', dashboard_api.get_collection, name='get_collection'),
  re_path(r'^get_collections$', dashboard_api.get_collections, name='get_collections'),
  re_path(r'^get_stats$', dashboard_api.get_stats, name='get_stats'),
  re_path(r'^get_terms$', dashboard_api.get_terms, name='get_terms'),
]
