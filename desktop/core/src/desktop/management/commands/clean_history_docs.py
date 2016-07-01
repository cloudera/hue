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
from datetime import datetime,  timedelta

from django.core.management.base import BaseCommand

from desktop.models import Document2


LOG = logging.getLogger(__name__)

DEFAULT_EXPIRY_DAYS = 120


class Command(BaseCommand):
  """
  Clean up (delete) history documents without a parent or that are older than N number of days.

  e.g.
  build/env/bin/hue clean_history_docs 30
  0 history documents deleted.
  """
  args = '<age_in_days> (default is %s)' % DEFAULT_EXPIRY_DAYS
  help = 'Delete history documents older than %s days.' % DEFAULT_EXPIRY_DAYS

  def handle(self, *args, **options):
    count = 0
    days = int(args[0]) if len(args) >= 1 else DEFAULT_EXPIRY_DAYS

    # Clean up orphan history documents (excluding query docs)
    orphans = Document2.objects.exclude(type__startswith='query-').filter(is_history=True).filter(dependents=None)

    if orphans.count() > 0:
      count += orphans.count()
      self.stdout.write('Deleting %d orphan history documents...' % orphans.count())
      orphans.delete()
    else:
      self.stdout.write('No orphan history documents found.')

    # Clean up old history documents
    old_history_docs = Document2.objects.filter(is_history=True).filter(last_modified__lte=datetime.today() - timedelta(days=days))

    if old_history_docs.count() > 0:
      count += old_history_docs.count()
      self.stdout.write('Deleting %d history documents older than %d days...' % (old_history_docs.count(), days))
      old_history_docs.delete()
    else:
      self.stdout.write('No history documents older than %d days found.' % days)

    self.stdout.write('%d total history documents deleted.' % count)
