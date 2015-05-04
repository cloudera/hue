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

import json
import os
import sys

from django.utils.translation import ugettext_lazy as _t, ugettext as _

from desktop.lib.conf import Config, coerce_bool
from spark.settings import NICE_NAME


def coerce_json(j):
  return json.loads(j)


LANGUAGES = Config(
  key="languages",
  help=_t("List of available types of snippets."),
  type=coerce_json,
  default="""[
      {"name": "Scala", "type": "scala"},
      {"name": "Python", "type": "python"},
      {"name": "Impala SQL", "type": "impala"},
      {"name": "Hive SQL", "type": "hive"},
      {"name": "Text", "type": "text"}
  ]"""
)

LIVY_ASSEMBLY_JAR = Config(
  key="livy_assembly_jar",
  help=_t("Path to livy-assembly.jar"),
  private=True,
  default=os.path.join(os.path.dirname(__file__), "..", "..", "java-lib", "livy-assembly-3.7.0-cdh5.4.1.jar"))

LIVY_SERVER_HOST = Config(
  key="livy_server_host",
  help=_t("Host address of the Livy Server."),
  default="0.0.0.0")

LIVY_SERVER_PORT = Config(
  key="livy_server_port",
  help=_t("Port of the Livy Server."),
  default="8998")

LIVY_SERVER_SESSION_KIND = Config(
  key="livy_server_session_kind",
  help=_t("Configure livy to start with process, thread, or yarn workers"),
  default="process")

LIVY_YARN_JAR = Config(
  key="livy_yarn_jar",
  help=_t("Path to livy-assembly.jar inside HDFS"),
  private=True)

START_LIVY_SERVER = Config(
  key="start_livy_server",
  help=_t("Experimental option to launch livy"),
  default=False,
  type=coerce_bool,
  private=True)

def get_livy_server_url():
  return 'http://%s:%s' % (LIVY_SERVER_HOST.get(), LIVY_SERVER_PORT.get())

def get_spark_status(user):
  from spark.job_server_api import get_api
  status = None

  try:
    if not 'test' in sys.argv: # Avoid tests hanging
      get_api(user).get_status()
      status = 'OK'
  except:
    pass

  return status


def config_validator(user):
  res = []

  status = get_spark_status(user)

  if status != 'OK':
    res.append((NICE_NAME, _("The app won't work without a running Livy Spark Server")))

  return res
