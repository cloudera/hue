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

from django.utils.translation import ugettext_lazy as _

from desktop.lib.conf import Config, coerce_bool


HIVE_V1 = Config(
  key="hive_v1",
  help=_("Use Sentry API V1 for Hive."),
  default=True,
  type=coerce_bool)

HIVE_V2 = Config(
  key="hive_v2",
  help=_("Use Sentry generic API V2 for Hive."),
  default=False,
  type=coerce_bool)

SOLR_V2 = Config(
  key="solr_v2",
  help=_("Use Sentry generic API V2 for Solr."),
  default=True,
  type=coerce_bool)
