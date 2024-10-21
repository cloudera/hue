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
import logging

from django.utils.translation import gettext as _, gettext_lazy as _t

import beeswax.hive_site
from beeswax.settings import NICE_NAME
from desktop.conf import has_connectors
from desktop.lib.exceptions import StructuredThriftTransportException

LOG = logging.getLogger()


def config_validator(user):
  '''
  v2
  When using the connectors, now 'hive' is seen as a dialect and only the list of connections
  (instance of the 'hive' connector, e.g. pointing to a Hive server in the Cloud) should be tested.
  Interpreters are now tested by the Editor in libs/notebook/conf.py.

  v1
  All the configuration happens in apps/beeswax.
  '''
  from beeswax.design import hql_query  # dbms is dependent on beeswax.conf, import in method to avoid circular dependency
  from beeswax.server import dbms

  res = []

  if has_connectors():
    return res

  try:
    try:
      if 'test' not in sys.argv:  # Avoid tests hanging
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
    from aws.conf import is_enabled as is_s3_enabled
    from azure.conf import is_abfs_enabled
    from desktop.lib.fsmanager import get_filesystem
    warehouse = beeswax.hive_site.get_metastore_warehouse_dir()
    fs = get_filesystem()
    fs_scheme = fs._get_scheme(warehouse)
    if fs:
      if fs_scheme == 's3a':
        if is_s3_enabled():
          fs.do_as_user(user, fs.stats, warehouse)
        else:
          LOG.warning("Warehouse is in S3, but no credential available.")
      elif fs_scheme == 'abfs':
        if is_abfs_enabled():
          fs.do_as_user(user, fs.stats, warehouse)
        else:
          LOG.warning("Warehouse is in ABFS, but no credential available.")
      else:
        fs.do_as_superuser(fs.stats, warehouse)
  except Exception:
    msg = 'Failed to access Hive warehouse: %s'
    LOG.exception(msg % warehouse)
    res.append((NICE_NAME, _(msg) % warehouse))

  return res
