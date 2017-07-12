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
import json
import subprocess

from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException


LOG = logging.getLogger(__name__)


def _exec(args):
  try:
    data = subprocess.check_output([
        'altus',
        'wa',
       ] +
       args
    )
  except Exception, e:
    raise PopupException(e, title=_('Error accessing'))

  response = json.loads(data)

  return response


class WorkfloadAnalyticsClient():

  def __init__(self, user):
    self.user = user

  def get_operation_execution_details(self, operation_id):

    return WorkloadAnalytics(self.user).get_operation_execution_details(operation_id=operation_id, include_tree=True)


class WorkloadAnalytics():

  def __init__(self, user): pass

  def get_operation_execution_details(self, operation_id, include_tree=False):
    args = ['get-operation-execution-details', '--id', operation_id]

    if include_tree:
      args.append('--include-tree')

    return _exec(args)
