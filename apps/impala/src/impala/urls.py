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

from beeswax.urls import urlpatterns as beeswax_urls


urlpatterns = patterns('impala.views',
  url(r'^api/refresh_tables$', 'refresh_tables', name='refresh_tables'),

  url(r'^dashboard/$', 'dashboard', name='dashboard'),
  url(r'^dashboard/query', 'query', name='query'),
  
  url(r'^dashboard/new_facet$', 'new_facet', name='new_facet'),
  url(r'^dashboard/new_search$', 'new_search', name='new_search'),
  url(r'^dashboard/get_fields', 'get_fields', name='get_fields'),
)

urlpatterns += beeswax_urls
