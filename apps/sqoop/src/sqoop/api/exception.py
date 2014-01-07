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
import socket

from django.utils.translation import ugettext as _
from django.utils.encoding import smart_str


LOG = logging.getLogger(__name__)


def handle_rest_exception(e, msg):
  parent_ex = e.get_parent_ex()
  reason = None
  if hasattr(parent_ex, 'reason'):
    reason = parent_ex.reason
  if isinstance(reason, socket.error):
    LOG.error(smart_str('Could not connect to sqoop server: %s (%s)' % (reason[0], reason[1])))
    return {
      'status': -1,
      'errors': [_('Could not connect to sqoop server. %s (%s)') % (reason[0], reason[1])]
    }
  else:
    LOG.error(smart_str(msg))
    LOG.error(smart_str(e.message))
    return {
      'status': 1,
      'errors': [msg],
      'exception': str(e)
    }
