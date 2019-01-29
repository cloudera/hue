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

from django.conf.urls import url

from beeswax.urls import urlpatterns as beeswax_urls
from impala import api as impala_api

urlpatterns = [
  url(r'^api/invalidate$', impala_api.invalidate, name='invalidate'),
  url(r'^api/refresh/(?P<database>\w+)/(?P<table>\w+)$', impala_api.refresh_table, name='refresh_table'),
  url(r'^api/query/(?P<query_history_id>\d+)/exec_summary$', impala_api.get_exec_summary, name='get_exec_summary'),
  url(r'^api/query/(?P<query_history_id>\d+)/runtime_profile', impala_api.get_runtime_profile, name='get_runtime_profile'),
  url(r'^api/query/alanize$', impala_api.alanize, name='alanize'),
  url(r'^api/query/alanize/fix$', impala_api.alanize_fix, name='alanize_fix'),
  url(r'^api/query/alanize/metrics', impala_api.alanize_metrics, name='alanize_metrics'),
]

urlpatterns += beeswax_urls
