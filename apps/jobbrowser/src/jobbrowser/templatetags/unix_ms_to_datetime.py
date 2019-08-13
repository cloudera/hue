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

from __future__ import division
from past.utils import old_div
import datetime
import django
from django.utils.translation import ugettext as _

register = django.template.Library()

@register.filter(name='unix_ms_to_datetime')
def unix_ms_to_datetime(unixtime):
  """unixtime is seconds since the epoch"""
  if unixtime:
    return datetime.datetime.fromtimestamp(old_div(unixtime,1000))
  return _("No time")
unix_ms_to_datetime.is_safe = True


