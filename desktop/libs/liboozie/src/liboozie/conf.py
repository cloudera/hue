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


OOZIE_URL = Config(
  key='oozie_url',
  help=_('URL to Oozie server. This is required for job submission.'),
  default='http://localhost:11000/oozie',
  type=str)

SECURITY_ENABLED = Config(
  key="security_enabled",
  help=_("Whether Oozie requires client to do perform Kerberos authentication"),
  default=False,
  type=coerce_bool)

REMOTE_DEPLOYMENT_DIR = Config(
  key="remote_data_dir",
  default="/user/hue/oozie/deployments",
  help=_("Location on HDFS where the workflows/coordinator are deployed when submitted by a non owner."))
