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
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _t

from desktop.conf import LDAP

from useradmin import ldap_access
from useradmin.views import sync_ldap_users_and_groups

class Command(BaseCommand):
  """
  Handler for syncing the Hue database with LDAP users and groups.

  This will not import any users or groups that don't already exist in Hue. All
  user information and group memberships will be updated based on the LDAP
  server's current state.
  """
  def add_arguments(self, parser):
    parser.add_argument("--server", help=_t("Server to connect to."),
                              action="store",
                              default=None)

  def handle(self, **options):
    server = options['server']

    connection = ldap_access.get_connection_from_server(server)

    sync_ldap_users_and_groups(connection)
