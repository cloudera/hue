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

from desktop.lib.conf import Config, coerce_bool

if sys.version_info[0] > 2:
  from django.utils.translation import gettext_lazy as _
else:
  from django.utils.translation import ugettext_lazy as _


SOLR_URL = Config(
  key="solr_url",
  help=_("URL of the Solr Server."),
  default="http://localhost:8983/solr/")

EMPTY_QUERY = Config(
  key="empty_query",
  help=_("Query sent when no term is entered."),
  default="*:*")

SECURITY_ENABLED = Config(
  key="security_enabled",
  help=_("Whether Solr requires client to perform Kerberos authentication."),
  default=False,
  type=coerce_bool)

DOWNLOAD_LIMIT = Config(
  key="download_limit",
  help=_("Default 1000 rows, max is 15K rows."),
  default=1000,
  type=int)

# Unused: deprecated by dashboard
LATEST = Config(
  key="latest",
  help=_("Use latest Solr 5.2+ features."),
  default=False,
  type=coerce_bool)
