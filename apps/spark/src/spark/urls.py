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


# Views
urlpatterns = patterns('spark.views',
  url(r'^$', 'editor', name='index'),
  url(r'^editor$', 'editor', name='editor'),
  url(r'^list_notebooks$', 'list_notebooks', name='list_notebooks'),  
)

# APIs
urlpatterns += patterns('spark.api',
  url(r'^api/create_session$', 'create_session', name='create_session'),
  url(r'^api/execute$', 'execute', name='execute'),
  url(r'^api/check_status$', 'check_status', name='check_status'),
  url(r'^api/fetch_result_data$', 'fetch_result_data', name='fetch_result_data'),
  url(r'^api/fetch_result_metadata$', 'fetch_result_metadata', name='fetch_result_metadata'),
  url(r'^api/cancel_statement', 'cancel_statement', name='cancel_statement'),
  url(r'^api/get_log', 'get_log', name='get_log'),

  url(r'^api/notebook/save$', 'save_notebook', name='save_notebook'),
  url(r'^api/notebook/open$', 'open_notebook', name='open_notebook'),
)

