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
  url(r'^query$', 'index', name='query'),
  url(r'^admin$', 'admin', name='admin'),
  url(r'^admin/cores$', 'admin', name='admin_cores'),
  url(r'^admin/core/(?P<core>\w+)/properties$', 'admin_core_properties', name='admin_core_properties'),
  url(r'^admin/core/(?P<core>\w+)/schema$', 'admin_core_schema', name='admin_core_schema'),
  url(r'^admin/core/(?P<core>\w+)/template$', 'admin_core_template', name='admin_core_template'),
  url(r'^admin/core/(?P<core>\w+)/facets$', 'admin_core_facets', name='admin_core_facets'),
  url(r'^admin/core/(?P<core>\w+)/sorting$', 'admin_core_sorting', name='admin_core_sorting'),

)
