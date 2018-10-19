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
from django.core.management.base import BaseCommand
from django.db import transaction

from desktop.models import Directory, Document, Document2, Document2Permission, SAMPLE_USER_OWNERS
from useradmin.models import get_default_user_group, install_sample_user


LOG = logging.getLogger(__name__)


class Command(BaseCommand):
  def handle(self, *args, **options):

    sample_user = install_sample_user()

    # Get or create sample user directories
    home_dir = Directory.objects.get_home_directory(sample_user)
    examples_dir, created = Directory.objects.get_or_create(
      parent_directory=home_dir,
      owner=sample_user,
      name=Document2.EXAMPLES_DIR
    )

    if not Document2.objects.filter(type='search-dashboard', owner__username__in=SAMPLE_USER_OWNERS).exists():
      with transaction.atomic():
        management.call_command('loaddata', 'initial_search_examples.json', verbosity=2, commit=False)
        Document.objects.sync()

      Document2.objects.filter(type='search-dashboard', owner__username__in=SAMPLE_USER_OWNERS).update(parent_directory=examples_dir)
    else:
      # Check if sample documents are in Trash, and if so, restore them
      for doc in Document2.objects.filter(type='search-dashboard', owner__username__in=SAMPLE_USER_OWNERS):
        if doc.parent_directory != examples_dir:
          doc.parent_directory = examples_dir
          doc.save()

    # Share with default group
    examples_dir.share(sample_user, Document2Permission.READ_PERM, groups=[get_default_user_group()])
    LOG.info('Successfully installed sample search dashboard')
