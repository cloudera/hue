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

from beeswax.urls import urlpatterns as beeswax_urls
from impala import api as impala_api

if sys.version_info[0] > 2:
  from django.urls import re_path
else:
  from django.conf.urls import url as re_path

urlpatterns = [
  re_path(r'^api/invalidate$', impala_api.invalidate, name='invalidate'),
  re_path(r'^api/refresh/(?P<database>\w+)/(?P<table>\w+)$', impala_api.refresh_table, name='refresh_table'),
  re_path(r'^api/query/(?P<query_history_id>\d+)/exec_summary$', impala_api.get_exec_summary, name='get_exec_summary'),
  re_path(r'^api/query/(?P<query_history_id>\d+)/runtime_profile', impala_api.get_runtime_profile, name='get_runtime_profile'),
  re_path(r'^api/query/alanize$', impala_api.alanize, name='alanize'),
  re_path(r'^api/query/alanize/fix$', impala_api.alanize_fix, name='alanize_fix'),
  re_path(r'^api/query/alanize/metrics', impala_api.alanize_metrics, name='alanize_metrics'),
]

urlpatterns += beeswax_urls
