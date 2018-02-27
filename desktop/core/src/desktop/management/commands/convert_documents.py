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
import sys
import time

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from desktop.converters import DocumentConverter

class Command(BaseCommand):

  def handle(self, *args, **options):
    print 'Starting document conversions...\n'
    try:
      with transaction.atomic():
        users = User.objects.all()
        logging.info("Starting document conversions for %d users" % len(users))
        for index, user in enumerate(users):
          logging.info("Starting document conversion for user %d: %s" % (index, user.username))

          start_time = time.time()
          converter = DocumentConverter(user)
          converter.convert()
          logging.info("Document conversions for user:%s took %.3f seconds" % (user.username, time.time() - start_time))

          if converter.failed_doc_ids:
            print >> sys.stderr, 'Failed to import %d document(s) for user: %s - %s' % (len(converter.failed_doc_ids), user.username, converter.failed_doc_ids)
    except Exception, e:
      logging.exception("Failed to execute the document conversions.")

    print 'Finished running document conversions.\n'
