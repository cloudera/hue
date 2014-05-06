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


LOG = logging.getLogger(__name__)


class SentryApi(object):

  def __init__(self, client):
    """
    Parameters
    ----------
    client : SentryClient
      The sentry client
    """
    self.client = client

  def get_roles_for_table(self, database, table):
    roles = self.client.get_roles()

    # Fetch privileges and filter out roles that don't have privileges for this table
    old_roles = roles.copy()
    for role, properties in old_roles.items():
      properties['privileges'] = self.client.get_privileges_for_role(role)

      if not filter(lambda privilege: privilege['scope'].lower() == 'table' and privilege['database'] == database and privilege['table'] == table, roles[role]['privileges']):
        del roles[role]

    return roles

  def get_roles(self, database):
    roles = self.client.get_roles()
    return roles
