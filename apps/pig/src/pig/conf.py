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

from os.path import dirname, join
from django.utils.translation import ugettext_lazy as _

from desktop.lib.conf import Config


# TODO update hue.inis

REPO_PROTOCOL = Config(
  key="repo_protocol",
  help=_("Protocol of the repository URI (e.g. 'http://, file://)."),
  default='http://')

REPO_URI = Config(
  key="repo_uri",
  # TODO remove
  default=join(dirname(__file__), "..", "..", "src/pig/test_data/test-repo"),
  help=_("Path of the repository to fetch."))

HDFS_WORKSPACE = Config(
  key="hdfs_workspace",
  default="/tmp",
  help=_("Where to upload the demo and save their outputs."))
