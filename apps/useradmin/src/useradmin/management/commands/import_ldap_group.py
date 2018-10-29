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
from useradmin.views import import_ldap_groups

class Command(BaseCommand):
  """
  Handler for importing LDAP groups into the Hue database.

  If a group has been previously imported, this will sync membership within the
  group with the LDAP server. If --import-members is specified, it will import
  all unimported users.
  """
  def add_arguments(self, parser):
    parser.add_argument("--dn", help=_t("Whether or not the user should be imported by "
                               "distinguished name."),
                          action="store_true",
                          default=False)
    parser.add_argument("--import-members", help=_t("Import users from the group."),
                                      action="store_true",
                                      default=False)
    parser.add_argument("--import-members-recursive", help=_t("Import users from the group, but also do so recursively."),
                                                action="store_true",
                                                default=False)
    parser.add_argument("--sync-users", help=_t("Sync users in the group."),
                                  action="store_true",
                                  default=False)
    parser.add_argument("--server", help=_t("Server to connect to."),
                              action="store",
                              default=None)

  def handle(self, group=None, **options):
    if group is None:
      raise CommandError(_("A group name must be provided."))

    import_members = options['import_members']
    import_by_dn = options['dn']
    import_members_recursive = options['import_members_recursive']
    sync_users = options['sync_users']
    server = options['server']

    connection = ldap_access.get_connection_from_server(server)

    import_ldap_groups(connection, group, import_members, import_members_recursive, sync_users, import_by_dn)
