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

from desktop.api2 import api_error_handler
from desktop.lib.vcs.apis.base_api import get_api


@api_error_handler
def authorize(request):
  interface = request.GET.get('interface', 'git-read-only')
  return get_api(interface).authorize(request)

@api_error_handler
def contents(request):
  interface = request.GET.get('interface', 'git-read-only')
  return get_api(interface).contents(request)
