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

from django.contrib.auth.models import User

from desktop.conf import LDAP

from models import UserProfile
from views import import_ldap_users

import ldap_access


LOG = logging.getLogger(__name__)


class LdapSynchronizationMiddleware(object):
  """
  Synchronize against LDAP authority.
  """
  USER_CACHE_NAME = 'ldap_use_group_sync_cache'

  def process_request(self, request):
    user = request.user

    if not user or not user.is_authenticated():
      return

    if not User.objects.filter(username=user.username, userprofile__creation_method=str(UserProfile.CreationMethod.EXTERNAL)).exists():
      LOG.warn("User %s is not an Ldap user" % user.username)
      return

    # Cache should be cleared when user logs out.
    if self.USER_CACHE_NAME not in request.session:
      if LDAP.LDAP_SERVERS.get():
        connection = ldap_access.get_connection_from_server(next(LDAP.LDAP_SERVERS.__iter__()))
      else:
        connection = ldap_access.get_connection_from_server()
      request.session[self.USER_CACHE_NAME] = import_ldap_users(connection, user.username, sync_groups=True, import_by_dn=False)
      request.session.modified = True
