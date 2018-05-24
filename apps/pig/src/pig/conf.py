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
import sys

from django.utils.translation import ugettext as _, ugettext_lazy as _t

from desktop.lib.conf import Config
from liboozie.conf import get_oozie_status

from pig.settings import NICE_NAME


LOCAL_SAMPLE_DIR = Config(
  key="local_sample_dir",
  default=os.path.join(os.path.dirname(__file__), "..", "..", "examples"),
  help=_t("Path to directory with piggybank.jar on local filesystem."),
  private=True)

REMOTE_SAMPLE_DIR = Config(
  key="remote_data_dir",
  default="/user/hue/pig/examples",
  help=_t("Location on HDFS where the Pig examples are stored."))


def config_validator(user):
  res = []

  if not 'test' in sys.argv: # Avoid tests hanging
    status = get_oozie_status(user)

    if 'NORMAL' not in status:
      res.append((NICE_NAME, _("The app won't work without a running Oozie server")))

  return res
