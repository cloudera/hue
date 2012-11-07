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

from django.utils.translation import ugettext as _, ugettext_lazy as _t

from desktop.lib.conf import Config, coerce_bool, validate_path


OOZIE_URL = Config(
  key='oozie_url',
  help=_t('URL to Oozie server. This is required for job submission.'),
  default='http://localhost:11000/oozie',
  type=str)

SECURITY_ENABLED = Config(
  key="security_enabled",
  help=_t("Whether Oozie requires client to perform Kerberos authentication"),
  default=False,
  type=coerce_bool)

REMOTE_DEPLOYMENT_DIR = Config(
  key="remote_deployement_dir",
  default="/user/hue/oozie/deployments",
  help=_t("Location on HDFS where the workflows/coordinator are deployed when submitted by a non owner."))



def config_validator():
  """
  config_validator() -> [ (config_variable, error_message) ]

  Called by core check_config() view.
  """
  from hadoop.cluster import get_all_hdfs
  from liboozie.oozie_api import get_oozie

  res = []

  status = 'down'
  try:
    status = str(get_oozie().get_oozie_status())
  except:
    pass
  if 'NORMAL' not in status:
    res.append((status, _('The Oozie server is not available')))


  class ConfigMock:
    def __init__(self, value): self.value = value
    def get(self): return self.value
    def get_fully_qualifying_key(self): return self.value

  for cluster in get_all_hdfs().values():
    res.extend(validate_path(REMOTE_DEPLOYMENT_DIR, is_dir=True, fs=cluster,
                             message=_('The deployment directory of Oozie workflows does not exist. '
                                       'Please run "Setup App" on the Oozie workflow page.')))
    res.extend(validate_path(ConfigMock('/user/oozie/share/lib'), is_dir=True, fs=cluster,
                             message=_('Oozie Share Lib not installed in default location.')))

  return res
