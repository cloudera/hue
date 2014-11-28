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
  url(r'^editor/design/(?P<design_id>.+)$', 'editor', name='execute_design'), # For Beeswax
  url(r'^editor/query/(?P<query_history_id>.+)$', 'editor', name='watch_query_history'), # For Beeswax
  url(r'^editor/(?P<design_id>.+)?$', 'editor', name='view_job'), # For browser
  url(r'^editor/(?P<design_id>.+)?$', 'editor', name='editor'),
  url(r'^editor/(?P<design_id>.+)?$', 'editor', name='execute_query'), # For Beeswax
  url(r'^list_jobs', 'list_jobs', name='list_jobs'),
  url(r'^list_contexts', 'list_contexts', name='list_contexts'),
  url(r'^delete_contexts', 'delete_contexts', name='delete_contexts'),
  url(r'^list_applications', 'list_applications', name='list_applications'),
  url(r'^upload_app$', 'upload_app', name='upload_app'),
  url(r'^download_result/(?P<job_id>.+)?$', 'download_result', name='download_result'),
)

# APIs
urlpatterns += patterns('spark.api',
  url(r'^api/execute$', 'execute', name='execute'),
  url(r'^api/check_status', 'check_status', name='check_status'),
  url(r'^api/fetch_result$', 'fetch_result', name='fetch_result'),
                        
  url(r'^api/jars$', 'jars', name='jars'),  
  url(r'^api/contexts$', 'contexts', name='contexts'),
  url(r'^api/job/(?P<job_id>.+)$', 'job', name='job'),
  url(r'^api/create_context$', 'create_context', name='create_context'),
  url(r'^api/delete_context', 'delete_context', name='delete_context'),
  url(r'^api/save_query/((?P<design_id>\d+)/?)?$', 'save_query', name='save_query'),
)

urlpatterns += patterns('beeswax.views',
  url(r'^my_queries$', 'my_queries', name='my_queries'),
  url(r'^list_designs$', 'list_designs', name='list_designs'),
  url(r'^list_trashed_designs$', 'list_trashed_designs', name='list_trashed_designs'),
  url(r'^delete_designs$', 'delete_design', name='delete_design'),
  url(r'^restore_designs$', 'restore_design', name='restore_design'),
  url(r'^clone_design/(?P<design_id>\d+)$', 'clone_design', name='clone_design'),
  url(r'^query_history$', 'list_query_history', name='list_query_history')
)
