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
from builtins import object

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import smart_unicode

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _


def get_api(user, interface):
  if interface == 'navopt':
    from metadata.optimizer.optimizer_client import OptimizerClient
    return OptimizerClient(user)
  elif interface == 'optimizer':
    from metadata.optimizer.optimizer_rest_client import OptimizerRestClient
    return OptimizerRestClient(user)
  elif interface == 'dummy':
    from metadata.optimizer.dummy_client import DummyClient
    return DummyClient(user=user)
  else:
    raise PopupException(_('Optimizer connector interface not recognized: %s') % interface)


class OptimizerApiException(Exception):
  def __init__(self, message=None):
    self.message = message or _('No error message, please check the logs.')

  def __str__(self):
    return str(self.message)

  def __unicode__(self):
    return smart_unicode(self.message)


def check_privileges(view_func):
  def decorate(*args, **kwargs):

    if OPTIMIZER.APPLY_SENTRY_PERMISSIONS.get():
      checker = get_checker(user=args[0].user)
      action = 'SELECT'
      objects = []

      if kwargs.get('db_tables'):
        for db_table in kwargs['db_tables']:
          objects.append({
              'server': get_hive_sentry_provider(),
              'db': _get_table_name(db_table)['database'],
              'table': _get_table_name(db_table)['table']
            }
          )
      else:
        objects = [{'server': get_hive_sentry_provider()}]

        if kwargs.get('database_name'):
          objects[0]['db'] = kwargs['database_name']
        if kwargs.get('table_name'):
          objects[0]['table'] = kwargs['table_name']

      filtered = list(checker.filter_objects(objects, action))

      if len(filtered) != len(objects):
        raise MissingSentryPrivilegeException({
            'pre_filtering': objects,
            'post_filtering': filtered,
            'diff': len(objects) - len(filtered)
          }
        )

    return view_func(*args, **kwargs)
  return wraps(view_func)(decorate)


class Api(object):
  '''
  Base Api
  '''

  def __init__(self, user=None):
    self.user = user

  # To implement


def _get_table_name(path):
  column = None

  if path.count('.') == 1:
    database, table = path.split('.', 1)
  elif path.count('.') == 2:
    database, table, column = path.split('.', 2)
  else:
    database, table = 'default', path

  name = {'database': database, 'table': table}
  if column:
    name['column'] = column

  return name
