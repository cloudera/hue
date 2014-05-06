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
import os

from desktop.lib import thrift_util

sys.path.append(os.path.join(os.path.dirname(__file__), '../../gen-py'))

from sentry_policy_service import SentryPolicyService, ttypes


LOG = logging.getLogger(__name__)

"""
from libsentry import api
from django.contrib.auth.models import User
user = User.objects.all()[0]
c = api.SentryApi('solaris.abe.cloudera.com', 10001, user)
response = c.get_roles()
response = c.get_privileges_for_role('test')
"""


class SentryClient(object):

  def __init__(self, host, port, user):
    """
    Client for the sentry service.

    Keyword arguments:
    host       -- `host` the server is listening on
    port       -- `port` the server is listening on
    user       -- Django `user` object
    """
    # @TODO(Abe) Kerberos
    self.user = user

    self.client = thrift_util.get_client(SentryPolicyService.Client,
                                         host,
                                         port,
                                         service_name="SentryPolicyService",
                                         username=self.user.username,
                                         timeout_seconds=30,
                                         multiple=True)

  def roles(self):
    """
    Fetch a mapping of roles to groups.
    """
    request = ttypes.TListSentryRolesRequest(requestorUserName=self.user.username, requestorGroupNames=[group.name for group in self.user.groups.all()])
    response = self.client.list_sentry_roles_by_group(request)
    if response.status.value == 0:
      roles = {}
      for role in response.roles:
        roles[role.roleName] = {
          'grantor': role.grantorPrincipal,
          'groups': [group.groupName for group in role.groups]
        }
      return roles
    else:
      raise RuntimeError(response.status.message)

  def privileges_for_role(self, role):
    """
    Fetch the privileges for a role.

    Keyword arguments:
    role     -- The `role` to fetch privileges for.
    """
    request = ttypes.TListSentryPrivilegesRequest(requestorUserName=self.user.username, requestorGroupNames=[group.name for group in self.user.groups.all()], roleName=role)
    response = self.client.list_sentry_privileges_by_role(request)
    if response.status.value == 0:
      priviliges = []
      for privilige in response.privileges:
        priviliges.append({
          'scope': privilige.privilegeScope,
          'name': privilige.privilegeName,
          'server': privilige.serverName,
          'database': privilige.dbName,
          'table': privilige.tableName,
          'URI': privilige.URI,
          'action': privilige.action,
          'timestamp': privilige.createTime,
          'grantor': privilige.grantorPrincipal
        })
      return priviliges
    else:
      raise RuntimeError(response.status.message)
