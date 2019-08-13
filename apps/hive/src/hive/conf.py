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
import sys

import beeswax.hive_site

from django.utils.translation import ugettext_lazy as _t, ugettext as _

from desktop.lib.exceptions import StructuredThriftTransportException
from beeswax.settings import NICE_NAME


LOG = logging.getLogger(__name__)


#
# All the configuration happens in apps/beeswax.
#


def config_validator(user):
  # dbms is dependent on beeswax.conf (this file)
  # import in method to avoid circular dependency
  from beeswax.design import hql_query
  from beeswax.server import dbms

  res = []
  try:
    try:
      if not 'test' in sys.argv: # Avoid tests hanging
        server = dbms.get(user)
        query = hql_query("SELECT 'Hello World!';")
        handle = server.execute_and_wait(query, timeout_sec=10.0)

        if handle:
          server.fetch(handle, rows=100)
          server.close(handle)
    except StructuredThriftTransportException as e:
      if 'Error validating the login' in str(e):
        msg = 'Failed to authenticate to HiveServer2, check authentication configurations.'
        LOG.exception(msg)
        res.append((NICE_NAME, _(msg)))
      else:
        raise e
  except Exception as e:
    msg = "The application won't work without a running HiveServer2."
    LOG.exception(msg)
    res.append((NICE_NAME, _(msg)))

  try:
    from desktop.lib.fsmanager import get_filesystem
    warehouse = beeswax.hive_site.get_metastore_warehouse_dir()
    fs = get_filesystem()
    fs.do_as_superuser(fs.stats, warehouse)
  except Exception:
    msg = 'Failed to access Hive warehouse: %s'
    LOG.exception(msg % warehouse)

    return [(NICE_NAME, _(msg) % warehouse)]

  return res
