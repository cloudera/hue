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

from desktop.lib.conf import Config, coerce_bool, ConfigSection

if sys.version_info[0] > 2:
  from django.utils.translation import gettext_lazy as _
else:
  from django.utils.translation import ugettext_lazy as _


SHARE_JOBS = Config(
  key='share_jobs',
  default=True,
  type=coerce_bool,
  help=_('Share submitted jobs information with all users. If set to false, '
       'submitted jobs are visible only to the owner and administrators.')
)

DISABLE_KILLING_JOBS = Config(
  key='disable_killing_jobs',
  default=False,
  type=coerce_bool,
  help=_('Disable the job kill button for all users in the job browser.')
)

LOG_OFFSET = Config(
  key='log_offset',
  default=-1000000,
  type=int,
  help=_('Offset in bytes where a negative offset will fetch the last N bytes for the given log file (default 1MB).')
)

# Deprecated
ENABLE_V2 = Config(
  key="enable_v2",
  help=_("Show the version 2 of app which unifies all the past browsers into one."),
  type=coerce_bool,
  default=True
)

MAX_JOB_FETCH = Config(
  key='max_job_fetch',
  default=500,
  type=int,
  help=_('Maximum number of jobs to fetch and display when pagination is not supported for the type.')
)

# Deprecated
ENABLE_QUERY_BROWSER = Config(
  key="enable_query_browser",
  help=_("Show the Impala query section for listing and showing more troubleshooting information."),
  type=coerce_bool,
  default=True
)

ENABLE_HIVE_QUERY_BROWSER = Config(
  key="enable_hive_query_browser",
  help=_("Show the Hive section for listing the query history and providing more troubleshooting information."),
  type=coerce_bool,
  default=False
)

ENABLE_QUERIES_LIST = Config(
  key="enable_queries_list",
  help=_("Show the Queries section for listing Hive/Impala query history and providing more troubleshooting information."),
  type=coerce_bool,
  default=False
)

ENABLE_HISTORY_V2 = Config(
  key="enable_history_v2",
  help=_("Show the version 2 of job/query History which unifies the all into one."),
  type=coerce_bool,
  default=False
)

QUERY_STORE = ConfigSection(
  key="query_store",
  help=_("""Credentials for query store API."""),
  members=dict(
    SERVER_URL=Config(
      key="server_url",
      default='http://localhost:8080/',
      help=_("URL of Query Store API server.")
    )
  )
)

USE_PROXY = Config(
  key="use_proxy",
  help=_("Use the proxy API instead of the ORM to access the query_store."),
  type=coerce_bool,
  default=True
)
