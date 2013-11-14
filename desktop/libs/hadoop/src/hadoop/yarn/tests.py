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

import logging

from hadoop.yarn.resource_manager_api import get_resource_manager


LOG = logging.getLogger(__name__)


def test_yarn_configurations():
  # Single cluster for now

  result = []

  try:
    url = ''
    api = get_resource_manager()
    url = api._url
    api.apps()
  except Exception, e:
    msg = 'Failed to contact Resource Manager at %s: %s' % (url, e)
    result.append(('Resource Manager', msg))

  return result
