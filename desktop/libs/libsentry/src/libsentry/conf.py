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
import os

from django.utils.translation import ugettext_lazy as _t
from desktop.lib.conf import Config


LOG = logging.getLogger(__name__)


HOSTNAME=Config(
  key='hostname',
  help=_t('Hostname or IP of server.'),
  type=str,
  default='localhost',
)

PORT=Config(
  key='port',
  help=_t('Port the sentry service is running on.'),
  type=int,
  default=8038,
)

SENTRY_CONF_DIR = Config(
  key='sentry_conf_dir',
  help=_t('Sentry configuration directory, where sentry-site.xml is located.'),
  default=os.environ.get("SENTRY_CONF_DIR", '/etc/sentry/conf')
)

PRIVILEGE_CHECKER_CACHING=Config(
  key='privilege_checker_caching',
  help=_t('Number of seconds when the privilege list of a user is cached.'),
  type=int,
  default=60 * 5,
)


def is_enabled():
  from hadoop import cluster # Avoid dependencies conflicts
  cluster = cluster.get_cluster_conf_for_job_submission()

  return HOSTNAME.get() != 'localhost' and cluster.SECURITY_ENABLED.get()
