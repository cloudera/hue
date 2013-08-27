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

from desktop.lib.conf import Config
from desktop.lib import paths
from django.utils.translation import ugettext_lazy as _


LOCAL_DATA_DIR = Config(
  key="local_data_dir",
  default=os.path.join(os.path.dirname(__file__), "..", "..", "data"),
  help=_("Location on local filesystem where examples and template are stored."),
  private=True)

SAMPLE_DATA_DIR = Config(
  key="sample_data_dir",
  default=paths.get_thirdparty_root("sample_data"),
  help=_("Location on local filesystem where sample data is stored."),
  private=True)
