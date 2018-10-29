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
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _t, ugettext as _

from desktop.conf import LDAP

from useradmin import ldap_access
from useradmin.views import import_ldap_users

class Command(BaseCommand):
  """
  Handler for importing LDAP users into the Hue database.

  If a user has been previously imported, this will sync their user information.
  """
  def add_arguments(self, parser):
      parser.add_argument("--dn", help=_t("Whether or not the user should be imported by "
                               "distinguished name."),
                          action="store_true",
                          default=False)
      parser.add_argument("--sync-groups", help=_t("Sync groups of the users."),
                                   action="store_true",
                                   default=False)
      parser.add_argument("--server", help=_t("Server to connect to."),
                              action="store",
                              default=None)

  def handle(self, user=None, **options):
    if user is None:
      raise CommandError(_("A username must be provided."))

    import_by_dn = options['dn']
    sync_groups = options['sync_groups']
    server = options['server']

    connection = ldap_access.get_connection_from_server(server)

    import_ldap_users(connection, user, sync_groups, import_by_dn)
