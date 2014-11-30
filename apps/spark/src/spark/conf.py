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

import sys

from django.utils.translation import ugettext_lazy as _t, ugettext as _

from desktop.lib.conf import Config
from spark.settings import NICE_NAME


JOB_SERVER_URL = Config(
  key="server_url",
  help=_t("URL of the Spark Job Server."),
  default="http://localhost:8080/"
)



def get_spark_status(user):
  from spark.job_server_api import get_api
  status = None

  try:
    if not 'test' in sys.argv: # Avoid tests hanging
      status = str(get_api(user).get_status())
  except ValueError:
    # No json returned
    status = 'OK'
  except:
    pass

  return status


def config_validator(user):
  res = []

  status = get_spark_status(user)

  if status != 'OK':
    res.append((NICE_NAME, _("The app won't work without a running Job Server")))

  return res
