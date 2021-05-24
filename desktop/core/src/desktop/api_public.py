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

from rest_framework.decorators import api_view

from notebook import api as notebook_api


@api_view(["POST"])
def create_notebook(request):
  return notebook_api.create_notebook(request)


@api_view(["POST"])
def autocomplete(request, server=None, database=None, table=None, column=None, nested=None):
  django_request = request._request
  return notebook_api.autocomplete(django_request, server, database, table, column, nested)
