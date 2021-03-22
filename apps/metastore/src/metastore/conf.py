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

from desktop.lib.conf import Config

if sys.version_info[0] > 2:
  from django.utils.translation import gettext_lazy as _
else:
  from django.utils.translation import ugettext_lazy as _


ENABLE_NEW_CREATE_TABLE = Config(
  key="enable_new_create_table",
  help=_("Flag to turn on the new version of the create table wizard."),
  type=bool,
  default=True
)

FORCE_HS2_METADATA = Config(
  key="force_hs2_metadata",
  help=_("Flag to force all metadata calls (e.g. list tables, table or column details...) to happen via HiveServer2 if available instead of Impala."),
  type=bool,
  default=False
)

SHOW_TABLE_ERD = Config(
  key="show_table_erd",
  default=False,
  type=bool,
  help=_('Choose whether to show the table ERD component.')
)
