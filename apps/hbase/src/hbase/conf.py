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

from __future__ import print_function
from builtins import str
import logging
import os
import sys

from django.utils.translation import ugettext_lazy as _t, ugettext as _

from desktop.conf import default_ssl_validate
from desktop.lib.conf import Config, validate_thrift_transport, coerce_bool
from hbase.hbase_site import get_thrift_transport


LOG = logging.getLogger(__name__)


HBASE_CLUSTERS = Config(
  key="hbase_clusters",
  default="(Cluster|localhost:9090)",
  help=_t("Comma-separated list of HBase Thrift servers for clusters in the format of '(name|host:port)'. Use full hostname with security."
          "Prefix hostname with https:// if using SSL and http mode with impersonation."),
  type=str
)

TRUNCATE_LIMIT = Config(
  key="truncate_limit",
  default="500",
  help=_t("Hard limit of rows or columns per row fetched before truncating."),
  type=int
)

THRIFT_TRANSPORT = Config(
  key="thrift_transport",
  default="buffered",
  help=_t("Should come from hbase-site.xml, do not set. 'framed' is used to chunk up responses, used with the nonblocking server in Thrift but is not supported in Hue."
       "'buffered' used to be the default of the HBase Thrift Server. Default is buffered when not set in hbase-site.xml."),
  type=str
)

HBASE_CONF_DIR = Config(
  key='hbase_conf_dir',
  help=_t('HBase configuration directory, where hbase-site.xml is located.'),
  default=os.environ.get("HBASE_CONF_DIR", '/etc/hbase/conf')
)

# Hidden, just for making patching of older version of Hue easier. To remove in Hue 4.
USE_DOAS = Config(
  key='use_doas',
  help=_t('Should come from hbase-site.xml, do not set. Force Hue to use Http Thrift mode with doas impersonation, regarless of hbase-site.xml properties.'),
  default=False,
  type=coerce_bool
)

SSL_CERT_CA_VERIFY = Config(
  key="ssl_cert_ca_verify",
  help=_t("Choose whether Hue should validate certificates received from the server."),
  dynamic_default=default_ssl_validate,
  type=coerce_bool
)


def config_validator(user):
  res = []

  from hbase.api import HbaseApi
  from hbase.settings import NICE_NAME

  try:
    if not 'test' in sys.argv: # Avoid tests hanging
      api = HbaseApi(user=user)
      cluster_name = api.getClusters()[0]['name'] # Currently pick first configured cluster
      # Check connectivity
      api.connectCluster(cluster_name)
      api.getTableList(cluster_name)
  except Exception as e:
    print(e)
    if 'Could not connect' in str(e):
      msg = "The application won't work without a running HBase Thrift Server v1."
    else:
      msg = 'Failed to authenticate to HBase Thrift Server, check authentication configurations.'
    LOG.exception(msg)
    res.append((NICE_NAME, _(msg)))

  if get_thrift_transport() == "framed":
    msg = "Hbase config thrift_transport=framed is not supported"
    LOG.exception(msg)
    res.append((NICE_NAME, _(msg)))



  res.extend(validate_thrift_transport(THRIFT_TRANSPORT))

  return res
