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

from django.db import connection, models, transaction
from django.db.models import Q
from django.db.models.query import QuerySet
from django.utils.translation import ugettext as _, ugettext_lazy as _t


# TODO: persistence and migrations

# class Connectors(models.Model):
#   type = models.CharField(max_length=32, db_index=True, help_text=_t('Type of connector, e.g. hive-tez, '))  # Must be in lib

#   name = models.CharField(default='', max_length=255)
#   description = models.TextField(default='')
#   uuid = models.CharField(default=uuid_default, max_length=36, db_index=True)

#   category = models.CharField(max_length=32, db_index=True, help_text=_t('Type of connector, e.g. query, browser, catalog...'))
#   interface = models.CharField(max_length=32, db_index=True, help_text=_t('Type of connector, e.g. hiveserver2'))

#   settings = models.TextField(default='{}')

#   last_modified = models.DateTimeField(auto_now=True, db_index=True, verbose_name=_t('Time last modified'))
