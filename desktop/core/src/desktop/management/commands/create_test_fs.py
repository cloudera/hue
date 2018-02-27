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

from django.core.management.base import BaseCommand

from desktop.lib.paths import get_build_dir
from hadoop.fs import fs_for_testing
from django.utils.translation import ugettext as _

class Command(BaseCommand):
  """Creates file system for testing."""
  def handle(self, *args, **options):
    fs_dir = os.path.join(get_build_dir(), "fs")
    if not os.path.isdir(fs_dir):
      os.makedirs(fs_dir)
    fs_for_testing.create(fs_dir)
    print _("Created fs in: %(dir)s") % {'dir': fs_dir}
