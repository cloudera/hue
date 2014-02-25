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

from django.contrib.auth.models import User
from django.core import management
from django.core.management.base import NoArgsCommand
from django.utils.translation import ugettext as _

from desktop.models import Document
from useradmin.models import install_sample_user

LOG = logging.getLogger(__name__)

# initial_search_examples.json: add 1000000 to the ids

class Command(NoArgsCommand):
  def handle_noargs(self, **options):

    # Load jobs
#    install_sample_user()
    management.call_command('loaddata', 'initial_search_examples.json', verbosity=2)
    Document.objects.sync()
