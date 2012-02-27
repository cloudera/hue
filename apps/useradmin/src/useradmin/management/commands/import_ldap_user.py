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
from optparse import make_option

from useradmin.views import import_ldap_user

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
  """
  Handler for importing LDAP users into the Hue database.

  If a user has been previously imported, this will sync their user information.
  """

  option_list = BaseCommand.option_list + (
      make_option("--dn", help="Whether or not the user should be imported by "
                               "distinguished name",
                          action="store_true",
                          default=False),
  )

  args = "username"

  def handle(self, user=None, **options):
    if user is None:
      raise CommandError("A username must be provided")

    import_by_dn = options['dn']
    import_ldap_user(user, import_by_dn)
