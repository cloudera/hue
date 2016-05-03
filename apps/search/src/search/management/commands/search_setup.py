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

from django.core import management
from django.core.management.base import NoArgsCommand

from desktop.models import Directory, Document, Document2, Document2Permission, SAMPLE_USER_OWNERS
from useradmin.models import get_default_user_group, install_sample_user


LOG = logging.getLogger(__name__)


class Command(NoArgsCommand):
  def handle_noargs(self, **options):

    if not Document2.objects.filter(type='search-dashboard', owner__username__in=SAMPLE_USER_OWNERS).exists():
      sample_user = install_sample_user()

      management.call_command('loaddata', 'initial_search_examples.json', verbosity=2)
      Document.objects.sync()

      # Get or create sample user directories
      home_dir = Directory.objects.get_home_directory(sample_user)
      examples_dir, created = Directory.objects.get_or_create(
        parent_directory=home_dir,
        owner=sample_user,
        name=Document2.EXAMPLES_DIR
      )

      Document2.objects.filter(type='search-dashboard', owner__username__in=SAMPLE_USER_OWNERS).update(parent_directory=examples_dir)

      # Share with default group
      examples_dir.share(sample_user, Document2Permission.READ_PERM, groups=[get_default_user_group()])
      LOG.info('Successfully installed sample search dashboard')
