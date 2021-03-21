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
import os

from django.core.management.base import BaseCommand

from desktop.lib.connectors.models import _get_installed_connectors
from beeswax.management.commands.beeswax_install_examples import Command as EditorCommand
from useradmin.models import User


LOG = logging.getLogger(__name__)


class Command(BaseCommand):
  args = '<user>'
  help = 'Install examples but do not overwrite them.'

  def add_arguments(self, parser):
    parser.add_argument(
        '--username',
        dest='username',
        default='hue',
        help='Hue username used to execute the command',
    )
    parser.add_argument(
        '--dialect',
        dest='dialect',
        default=None,
        help='Dialect name we want to install the samples, all if not specified',
    )

  def handle(self, *args, **options):
    LOG.info('Installing %s examples as %s' % (options.get('dialect') or 'all', options['username']))

    user = User.objects.get(username=options['username'])
    dialect = options.get('dialect')

    dialects = [
      {
        'id': connector['id'],
        'dialect': connector['dialect']
      }
      for connector in _get_installed_connectors(category='editor')
      if dialect is None or connector['dialect'] == dialect
    ]

    tables = None

    for dialect in dialects:
      EditorCommand().handle(
        app_name=dialect['dialect'],  # Unused?
        user=user,
        tables=tables,
        dialect=dialect['dialect'],
        interpreter={'type': dialect['id']}
      )
