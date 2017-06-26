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
from urlparse import urlparse

from django.utils.translation import ugettext_lazy as _t

from desktop.lib.conf import Config, coerce_bool
from desktop.conf import default_ssl_validate
from libzookeeper.conf import ENSEMBLE


LOG = logging.getLogger(__name__)


SSL_CERT_CA_VERIFY = Config(
  key="ssl_cert_ca_verify",
  help=_t("In secure mode (HTTPS), if Solr SSL certificates have to be verified against certificate authority"),
  dynamic_default=default_ssl_validate,
  type=coerce_bool
)


def zkensemble_path():
  """
  Try to guess Solr path in ZooKeeper.
  """
  try:
    parsed = urlparse(ENSEMBLE.get())
    if parsed.port == 9983: # Standalone Solr cloud
      return ''
  except:
    LOG.warn('Failed to get Zookeeper ensemble path')

  return '/solr'


SOLR_ZK_PATH = Config(
  key="solr_zk_path",
  help=_t("Default path to Solr in ZooKeeper"),
  dynamic_default=zkensemble_path,
  type=str
)
