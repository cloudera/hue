
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

import json
import logging
import sys

from django.utils.functional import wraps

from desktop.auth.backend import is_admin, is_hue_admin
from desktop.conf import ENABLE_ORGANIZATIONS
from desktop.lib.exceptions_renderable import PopupException

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _


LOG = logging.getLogger(__name__)


def admin_required(f):
  @wraps(f)
  def wrapper(request, *args, **kwargs):
    if not is_admin(request.user):
      raise PopupException(_("You must be an admin."), error_code=401)

    return f(request, *args, **kwargs)
  return wrapper


def hue_admin_required(f):
  @wraps(f)
  def wrapper(request, *args, **kwargs):
    if not is_hue_admin(request.user):
      raise PopupException(_("You must be a Hue admin."), error_code=401)

    return f(request, *args, **kwargs)
  return wrapper
