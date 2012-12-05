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
from desktop.lib.exceptions_renderable import PopupException
from django.utils.translation import ugettext as _

try:
  from functools import wraps
except ImportError:
  from django.utils.functional import wraps

LOG = logging.getLogger(__name__)

def hue_permission_required(action, app):
  """
  Checks that the user has permissions to do
  action 'action' on app 'app'.

  Note that user must already be logged in.
  """
  def decorator(view_func):
    @wraps(view_func)
    def decorated(request, *args, **kwargs):
      if not request.user.has_hue_permission(action, app):
        raise PopupException(_("Permission denied (%(action)s/%(app)s).") % {'action': action, 'app': app})
      return view_func(request, *args, **kwargs)
    return decorated
  return decorator
