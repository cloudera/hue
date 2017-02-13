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

from django.utils.translation import ugettext_lazy as _

from desktop.conf import is_hue4
from desktop.lib.conf import Config, coerce_bool


IS_ENABLED = Config(
  key="is_enabled",
  help=_("Activate the app in the menu."),
  dynamic_default=is_hue4,
  private=True,
  type=coerce_bool)

# TODO [[interfaces]] instead
IS_SQL_ENABLED = Config(
  key="is_sql_enabled",
  help=_("Offer to use SQL engines to compute the dashboards."),
  dynamic_default=is_hue4,
  private=True,
  type=coerce_bool)
