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

from desktop.lib.conf import Config, coerce_bool
from django.utils.translation import ugettext_lazy as _


SHARE_JOBS = Config(
  key='share_jobs',
  default=True,
  type=coerce_bool,
  help=_('Share submitted jobs information with all users. If set to false, '
       'submitted jobs are visible only to the owner and administrators.'))

DISABLE_KILLING_JOBS = Config(
  key='disable_killing_jobs',
  default=False,
  type=coerce_bool,
  help=_('Disable the job kill button for all users in the job browser.'))

