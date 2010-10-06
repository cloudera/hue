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

urlpatterns = patterns('jframegallery',
  url(r'^$', 'views.index'),
  url(r'^flash.redirect.*$', 'views.flash_redirect'),
  url(r'^flash.*$', 'views.flash'),
  url(r'^error_404.*$', 'views.error_404'),
  url(r'^error_500.*$', 'views.error_500'),
  url(r'^error_real_500.*$', 'views.error_real_500'),
  url(r'^error_python.*$', 'views.error_python'),
  url(r'^error_redirect.*$', 'views.error_redirect'),
  url(r'^redirect_301.*$', 'views.redirect_301'),
  url(r'^forwarding.*$', 'views.forwarding'),
  url(r'^error_message_exception.*$', 'views.error_message_exception'),
  url(r'^error_popup_exception.*$', 'views.error_popup_exception'),
  url(r'^forms_with_dependencies.*$', 'views.forms_with_dependencies'),
  url(r'^html-table.treeview.ajax.*$', 'views.pstree'),
  url(r'^(?P<path>.*)$', 'views.show')
)
