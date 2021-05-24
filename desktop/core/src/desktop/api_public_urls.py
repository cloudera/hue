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

from desktop import api_public

if sys.version_info[0] > 2:
  from django.urls import re_path
else:
  from django.conf.urls import url as re_path


# New "query" API
# https://demo.gethue.com/api/query
#
# https://demo.gethue.com/api/query/execute/hive
# https://demo.gethue.com/api/query/status
# https://demo.gethue.com/api/query/result
# https://demo.gethue.com/api/query/logs
urlpatterns = [
  re_path(r'^query/create_notebook/?$', api_public.create_notebook, name='api_create_notebook'),
  re_path(r'^query/autocomplete/?$', api_public.autocomplete, name='api_autocomplete_databases'),
]

# Compatibility with private API
# https://demo.gethue.com/api/editor/execute/hive
urlpatterns += [
  re_path(r'^editor/create_notebook/?$', api_public.create_notebook, name='api_create_notebook'),
  re_path(r'^editor/autocomplete/?$', api_public.autocomplete, name='api_autocomplete_databases'),
]
