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

import logging
import sys

from desktop.lib.conf import Config, ConfigSection, coerce_bool

if sys.version_info[0] > 2:
  from django.utils.translation import gettext_lazy as _t
else:
  from django.utils.translation import ugettext_lazy as _t


LOG = logging.getLogger()


def has_kafka():
  return KAFKA.IS_ENABLED.get()

def has_kafka_api():
  return bool(KAFKA.API_URL.get())


KAFKA = ConfigSection(
  key='kafka',
  help=_t("""Configuration options for Kafka API integration"""),
  members=dict(
    IS_ENABLED=Config(
      key="is_enabled",
      help=_t("Enable the Kafka integration."),
      type=coerce_bool,
      default=False
    ),
    API_URL=Config(
      key='api_url',
      help=_t('URL of Kafka REST API.'),
      default=None
    ),
    KSQL_API_URL=Config(
      key='ksql_api_url',
      help=_t('URL of ksqlDB API.'),
      default='http://localhost:8088'
    ),
    SCHEMA_REGISTRY_API_URL=Config(
      key='schema_registry_api_url',
      help=_t('URL of Schema Registry API.'),
      default='http://localhost:8081'
    ),
  )
)
