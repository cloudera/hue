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

from libsentry.api import get_api


LOG = logging.getLogger(__name__)


PRIVILEGE_HIERARCHY = {
  'SELECT': 0,
  'INSERT': 1,
  'ALL': 2
}

SENTRY_PRIVILEGE_KEY = 'SENTRY_PRIVILEGE'


class PrivilegeChecker(object):
  """
  Given a user, checks and applies Sentry privilege and authorization rules against Sentry objects
  """

  def __init__(self, user):
    self.user = user
    self.api = get_api(self.user)
    self.user_roles = self.api.list_sentry_roles_by_group('*')  # Get all roles for user


  def filter_objects(self, authorizableSet, action='SELECT'):
    """
    Given a set of authorizable Sentry objects and an action requested, return a filtered set of objects that the user
    has privileges to perform the given action upon.
    """
    filtered_objects = []
    privileges = []

    for role in self.user_roles:
      role_privileges = self.api.list_sentry_privileges_by_role(role['name'])
      privileges.extend(role_privileges)  # This may result in duplicates but will get reduced in hierarchy tree

    privilege_hierarchy = self._to_privilege_hierarchy(privileges)
    action = action.upper()

    for authorizable in authorizableSet:
      if self._is_object_action_authorized(hierarchy=privilege_hierarchy, object=authorizable, action=action):
        filtered_objects.append(authorizable)

    return filtered_objects


  def _to_privilege_hierarchy(self, privileges):
    """
    TODO: Refactor this to be cleaner and more efficient (use defaultdict and avoid redundant-insertion)
    Converts a list of privileges to a hierarchical tree of privileges by object, where the privilege is stored into a
    key named SENTRY_PRIVILEGE_KEY.
    NOTE: This assumes no objects share the same name as SENTRY_PRIVILEGE_KEY
    """
    hierarchy = {}

    for privilege in privileges:
      if privilege['column']:
        if privilege['server'] not in hierarchy:
          hierarchy[privilege['server']] = {
            privilege['database']: {
              privilege['table']: {
                privilege['column']: {
                  SENTRY_PRIVILEGE_KEY: privilege
                }
              }
            }
          }
        elif privilege['database'] not in hierarchy[privilege['server']]:
          hierarchy[privilege['server']][privilege['database']] = {
            privilege['table']: {
              privilege['column']: {
                SENTRY_PRIVILEGE_KEY: privilege
              }
            }
          }
        elif privilege['table'] not in hierarchy[privilege['server']][privilege['database']]:
          hierarchy[privilege['server']][privilege['database']][privilege['table']] = {
            privilege['column']: {
              SENTRY_PRIVILEGE_KEY: privilege
            }
          }
        else:  # We don't need to check if column is in the hierarchy b/c it's the lowest level object
          hierarchy[privilege['server']][privilege['database']][privilege['table']][privilege['column']] = {
            SENTRY_PRIVILEGE_KEY: privilege
          }
      elif privilege['table']:
        if privilege['server'] not in hierarchy:
          hierarchy[privilege['server']] = {
            privilege['database']: {
              privilege['table']: {
                SENTRY_PRIVILEGE_KEY: privilege
              }
            }
          }
        elif privilege['database'] not in hierarchy[privilege['server']]:
          hierarchy[privilege['server']][privilege['database']] = {
            privilege['table']: {
              SENTRY_PRIVILEGE_KEY: privilege
            }
          }
        elif privilege['table'] not in hierarchy[privilege['server']][privilege['database']]:
          hierarchy[privilege['server']][privilege['database']][privilege['table']] = {
            SENTRY_PRIVILEGE_KEY: privilege
          }
        else:
          hierarchy[privilege['server']][privilege['database']][privilege['table']][SENTRY_PRIVILEGE_KEY] = privilege
      elif privilege['database']:
        if privilege['server'] not in hierarchy:
          hierarchy[privilege['server']] = {
            privilege['database']: {
              SENTRY_PRIVILEGE_KEY: privilege
            }
          }
        elif privilege['database'] not in hierarchy[privilege['server']]:
          hierarchy[privilege['server']][privilege['database']] = {
            SENTRY_PRIVILEGE_KEY: privilege
          }
        else:
          hierarchy[privilege['server']][privilege['database']][SENTRY_PRIVILEGE_KEY] = privilege
      else:  # Server scope privilege
        if privilege['server'] not in hierarchy:
          hierarchy[privilege['server']] = {
            SENTRY_PRIVILEGE_KEY: privilege
          }
        else:
          hierarchy[privilege['server']][SENTRY_PRIVILEGE_KEY] = privilege

    return hierarchy


  def _is_object_action_authorized(self, hierarchy, object, action='SELECT'):
    requested_action_level = PRIVILEGE_HIERARCHY[action]
    server, db, table, column = object['server'], object['db'], object['table'], object['column']

    # Initialize all privileges for all object levels to non-authorized by default
    privileges_applied = {
      'server': -1,
      'db': -1,
      'table': -1,
      'column': -1
    }

    if server:  # Get server-level privilege
      if server in hierarchy:
        if SENTRY_PRIVILEGE_KEY in hierarchy[server]:
          privileges_applied['server'] = PRIVILEGE_HIERARCHY[hierarchy[server][SENTRY_PRIVILEGE_KEY]['action']]
        if db and db in hierarchy[server]: # Get db-level privilege
          if SENTRY_PRIVILEGE_KEY in hierarchy[server][db]:
            privileges_applied['db'] = PRIVILEGE_HIERARCHY[hierarchy[server][db][SENTRY_PRIVILEGE_KEY]['action']]
          if table and table in hierarchy[server][db]:  # Get table-level privilege
            if SENTRY_PRIVILEGE_KEY in hierarchy[server][db][table]:
              privileges_applied['table'] = PRIVILEGE_HIERARCHY[hierarchy[server][db][table][SENTRY_PRIVILEGE_KEY]['action']]
            if column and column in hierarchy[server][db][table]:  # Get column-level privilege
              # Since column is the lowest level, it must have a SENTRY_PRIVILEGE set
              privileges_applied['column'] = PRIVILEGE_HIERARCHY[hierarchy[server][db][table][column][SENTRY_PRIVILEGE_KEY]['action']]

    # A privilege hierarchy exists and at least one of the granted privileges is greater than or equal to requested action
    is_authorized = privileges_applied and max(privileges_applied.values()) >= requested_action_level
    return is_authorized
