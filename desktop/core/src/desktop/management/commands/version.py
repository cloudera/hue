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

from django.conf import settings
from django.core.management.base import NoArgsCommand

from desktop.lib.paths import get_desktop_root


class Command(NoArgsCommand):

  def handle_noargs(self, **options):
    cdh_path = os.path.join(get_desktop_root(), '..', 'cloudera', 'cdh_version.properties')
    if os.path.exists(cdh_path):
      print open(cdh_path).read()
    else:
      print settings.HUE_DESKTOP_VERSION

