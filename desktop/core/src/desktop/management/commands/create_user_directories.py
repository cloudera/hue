
# adapted from django-extensions (http://code.google.com/p/django-command-extensions/)
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
from django.core.management.base import CommandError, BaseCommand
from django.utils.translation import ugettext_lazy as _

from desktop.models import Document2


LOG = logging.getLogger(__name__)


class Command(BaseCommand):
  """
  Creates home and Trash directories for users as needed, or specific user if username is provided

  If no arguments are provided, this command will loop through all users and create a home and Trash directory for the
  user if they don't exist. It will then move any orphan documents to the home directory.

  If --username is specified, it will only perform the operation for the specific user.
  """
  help = _("Creates home and Trash directories for users as needed, or specific user if username is provided.")
  def add_arguments(self, parser):
    parser.add_argument('--username', help=_("Username of user to create directories for."), action='store', default=None)

  def handle(self, *args, **options):
    users = User.objects.all()

    if options['username']:
      try:
        user = User.objects.get(username=options['username'])
        users = [user]
      except Exception, e:
        msg = 'Failed to get user with username %s: %s' % (options['username'], str(e))
        self.stdout.write(msg)
        LOG.exception(msg)

    for user in users:
      try:
        msg = 'Attempting to create user directories for user: %s' % user.username
        self.stdout.write(msg)
        LOG.debug(msg)
        Document2.objects.create_user_directories(user)
      except Exception, e:
        msg = 'Failed to create user directories for user %s: %s' % (user.username, str(e))
        self.stdout.write(msg)
        LOG.warn(msg)
