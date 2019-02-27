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

from django.utils.translation import ugettext as _, ugettext_lazy as _t

from desktop.lib.conf import Config, coerce_bool
from desktop.lib import paths
from liboozie.conf import get_oozie_status

from oozie.settings import NICE_NAME


DEFINITION_XSLT_DIR = Config(
  key="definition_xslt_dir",
  default=os.path.join(os.path.dirname(__file__), "importlib", "xslt"),
  help=_t("Location on local FS where the xslt files are stored for workflow import."),
  private=True
)

DEFINITION_XSLT2_DIR = Config(
  key="definition_xslt2_dir",
  default=os.path.join(os.path.dirname(__file__), "importlib", "xslt2"),
  help=_t("Location on local FS where the xslt files are stored for workflow import."),
  private=True
)

LOCAL_SAMPLE_DIR = Config(
  key="local_data_dir",
  default=os.path.join(os.path.dirname(__file__), "..", "..", "examples"),
  help=_t("Location on local filesystem where the examples are stored."),
  private=True
)

LOCAL_SAMPLE_DATA_DIR = Config(
  key="sample_data_dir",
  default=paths.get_thirdparty_root("sample_data"),
  help=_t("Location on local filesystem where the data for the examples is stored."),
  private=True
)

REMOTE_SAMPLE_DIR = Config(
  key="remote_data_dir",
  default="/user/hue/oozie/workspaces",
  help=_t("Location on HDFS where the Oozie workflows are stored. Parameters are $TIME and $USER, e.g. /user/$USER/hue/workspaces/workflow-$TIME")
)


def get_oozie_job_count():
  '''Returns the maximum of jobs fetched by the API depending on the Hue version'''
  return 100

OOZIE_JOBS_COUNT = Config(
  key='oozie_jobs_count',
  dynamic_default=get_oozie_job_count,
  type=int,
  help=_t('Maximum number of Oozie workflows or coodinators or bundles to retrieve in one API call.')
)

ENABLE_V2 = Config( # Until Hue 4
  key='enable_v2',
  default=True,
  type=coerce_bool,
  help=_t('Use version 2 of Editor.')
)

ENABLE_CRON_SCHEDULING = Config( # Until Hue 3.8
  key='enable_cron_scheduling',
  default=True,
  type=coerce_bool,
  help=_t('Use Cron format for defining the frequency of a Coordinator instead of the old frequency number/unit.')
)

ENABLE_OOZIE_BACKEND_FILTERING = Config(
  key='enable_oozie_backend_filtering',
  default=True,
  type=coerce_bool,
  help=_t('Flag to enable Oozie backend filtering instead of doing it at the page level in Javascript. Requires Oozie 4.3+.')
)

ENABLE_DOCUMENT_ACTION = Config(
  key="enable_document_action",
  help=_t("Flag to enable the saved Editor queries to be dragged and dropped into a workflow."),
  type=bool,
  default=True
)

ENABLE_IMPALA_ACTION = Config(
  key="enable_impala_action",
  help=_t("Flag to enable the Impala action."),
  type=bool,
  default=False
)

ENABLE_ALTUS_ACTION = Config(
  key="enable_altus_action",
  help=_t("Flag to enable the Altus action."),
  type=bool,
  default=False
)


def config_validator(user):
  res = []

  status = get_oozie_status(user)

  if 'NORMAL' not in status:
    res.append((NICE_NAME, _("The app won't work without a running Oozie server")))

  return res
