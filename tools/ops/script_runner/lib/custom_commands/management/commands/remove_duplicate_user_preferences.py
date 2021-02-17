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

import os
import logging

from django.core.management.base import BaseCommand, CommandError
from desktop.models import UserPreferences
from django.db import models, transaction
from django.contrib.auth.models import User


import desktop.conf

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Handler for deleting duplicate UserPreference objects
    """

    def handle(self, *args, **options):
        LOG.warn("Deleting ducpliate UserPreference objects")

        for user in User.objects.filter():
            duplicated_records = UserPreferences.objects \
               .values('user', 'key') \
               .annotate(key_count=models.Count('key')) \
               .filter(key_count__gt=1, user = user)
            # Delete all but the first document.
            for record in duplicated_records:
                preferences = UserPreferences.objects \
                    .values_list('id', flat=True) \
                    .filter(
                        user = user,
                        key = record['key'],
                    )[1:]
                preferences = list(preferences)
                LOG.warn("Deleting UserPreferences duplicate ids: %s" % preferences)
                UserPreferences.objects.filter(id__in=preferences).delete()


        transaction.commit()
