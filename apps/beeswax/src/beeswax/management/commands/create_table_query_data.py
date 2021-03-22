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

from builtins import str

import logging
import sys

from django.core.management.base import BaseCommand

from desktop.lib import django_mako
from beeswax.server import dbms
from beeswax.server.dbms import get_query_server_config

from beeswax.design import hql_query
from beeswax import hive_site
from useradmin.models import install_sample_user

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _


LOG = logging.getLogger(__name__)


class Command(BaseCommand):
  """
  Create table sys.query_data over hive.hook.proto.base-directory
  """
  args = ''
  help = 'Create table sys.query_data over hive.hook.proto.base-directory'


  def handle(self, *args, **options):
    create_table()


def create_table(user=None, query_server=None, table=None):
  if not user:
    user = install_sample_user()
  if not query_server:
    query_server = get_query_server_config('beeswax')
  if not table:
    base_dir = hive_site.get_hive_hook_proto_base_directory()
    if not base_dir:
      msg = _('Error creating table query_data hive.hook.proto.base-directory is not configured')
      LOG.error(msg)
      return False
    table = {
      'name': 'query_data',
      'external_location': base_dir
    }

  server = dbms.get(user, query_server)
  for query in ["create_table_query_data.mako", "msck.mako"]:
    proposed_query = django_mako.render_to_string(query, {'table': table})
    query = hql_query(proposed_query)
    try:
      handle = server.execute_and_wait(query)
      if not handle:
        LOG.error(_('Error executing %s: Operation timeout.' % query))
        return False
      server.close(handle)
    except Exception as ex:
      LOG.error(_('Error executing %(query)s: %(error)s.') % {'query': query, 'error': ex})
      return False

  LOG.info(_('Table query_data has been created successfully'))
  return True
