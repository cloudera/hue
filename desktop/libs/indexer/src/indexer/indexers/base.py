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

from desktop.conf import has_connectors
from desktop.lib.connectors.models import _get_installed_connectors
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import smart_unicode

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _


def get_api(user, connector_id):
  if has_connectors() and connector_id != 'dummy':
    connectors = _get_installed_connectors(user=user, connector_id=int(connector_id))
    connector = connectors[0]
    dialect = connector['dialect']
  else:
    connector = None  # Could get the interpreter if Connectors are off
    dialect = connector_id

  if dialect == 'dummy':
    return Base(user, connector_id)
  else:
    raise PopupException(_('Indexer connector dialect not recognized: %s') % dialect)


class Base():

  def __init__(self, user, connector_id):
    self.user = user
    self.connector_id = connector_id

  def index(self, source, destination, options=None): pass



class IndexerApiException(Exception):
  def __init__(self, message=None):
    self.message = message or _('No error message, please check the logs.')

  def __str__(self):
    return str(self.message)

  def __unicode__(self):
    return smart_unicode(self.message)
