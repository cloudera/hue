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
from useradmin.views import sync_unix_users_and_groups

from django.core.management.base import BaseCommand

from django.utils.translation import ugettext_lazy as _

class Command(BaseCommand):
  """
  Handler for syncing the Hue database with Unix users and groups
  """
  def add_arguments(self, parser):
    parser.add_argument("--min-uid", help=_("Minimum UID to import (Inclusive)."), default=500)
    parser.add_argument("--max-uid", help=_("Maximum UID to import (Exclusive)."), default=65334)
    parser.add_argument("--min-gid", help=_("Minimum GID to import (Inclusive)."), default=500)
    parser.add_argument("--max-gid", help=_("Maximum GID to import (Exclusive)."), default=65334)
    parser.add_argument("--check-shell", help=_("Whether or not to check that the user's shell is not /bin/false."), default=True)

  def handle(self, *args, **options):
    # Typically, system users are under 500 or 1000, depending on OS, and there
    # is usually a nobody user at the top of the ID space, so let's avoid those
    min_uid = options['min_uid']
    max_uid = options['max_uid']
    min_gid = options['min_gid']
    max_gid = options['max_gid']
    check_shell = options['check_shell']

    sync_unix_users_and_groups(min_uid, max_uid, min_gid, max_gid, check_shell)
