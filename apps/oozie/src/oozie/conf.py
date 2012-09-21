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

import os.path

from django.utils.translation import ugettext_lazy as _

from desktop.lib.conf import Config, coerce_bool
from desktop.lib import paths


LOCAL_SAMPLE_DIR = Config(
  key="local_data_dir",
  default=os.path.join(os.path.dirname(__file__), "..", "..", "examples"),
  help=_("Location on local FS where the examples are stored"),
  private=True)

LOCAL_SAMPLE_DATA_DIR = Config(
  key="sample_data_dir",
  default=paths.get_thirdparty_root("sample_data"),
  help=_("Location on local FS where the data for the examples is stored"),
  private=True)

REMOTE_SAMPLE_DIR = Config(
  key="remote_data_dir",
  default="/user/hue/oozie/workspaces",
  help=_("Location on HDFS where the oozie workflows are stored."))

SHARE_JOBS = Config(
  key='share_jobs',
  default=True,
  type=coerce_bool,
  help=_('Share workflows and coordinators information with all users. If set to false, '
         'they will be visible only to the owner and administrators.'))

OOZIE_JOBS_COUNT = Config(
  key='oozie_jobs_count',
  default=100,
  type=int,
  help=_('Maximum of Oozie workflows or coodinators to retrieve in one API call.'))
