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
import os
from urlparse import urlparse

from django.utils.translation import ugettext_lazy as _t

from desktop.lib.conf import Config

LOG = logging.getLogger(__name__)


def solrctl():
  """
  solrctl path
  """
  for dirname in os.environ.get('PATH', '').split(os.path.pathsep):
    path = os.path.join(dirname, 'solrctl')

    if os.path.exists(path):
      return path

  return None


def zkensemble():
  """
  ZooKeeper Ensemble
  """
  try:
    from zookeeper.conf import CLUSTERS
    clusters = CLUSTERS.get()
    if clusters['default'].HOST_PORTS.get() != 'localhost:2181':
      return '%s/solr' % clusters['default'].HOST_PORTS.get()
  except:
    LOG.exception('failed to get zookeeper ensemble')

  try:
    from search.conf import SOLR_URL
    parsed = urlparse(SOLR_URL.get())
    return "%s:2181/solr" % (parsed.hostname or 'localhost')
  except:
    LOG.exception('failed to get solr url')



ENABLE_NEW_INDEXER = Config(
  key="enable_new_indexer",
  help=_t("Flag to turn on the morphline based Solr indexer."),
  type=bool,
  default=False
)


# Unused
BATCH_INDEXER_PATH = Config(
  key="batch_indexer_path",
  help=_t("Batch indexer path in HDFS."),
  type=str,
  default="/var/lib/search/search-mr-job.jar")

CORE_INSTANCE_DIR = Config(
  key="core_instance_dir",
  help=_t("Local path to Hue folder where Solr instance directories will be created in non-solrcloud mode."),
  type=str,
  default=os.path.join(os.path.dirname(__file__), '../data/collections'))

CONFIG_TEMPLATE_PATH = Config(
  key="config_template_path",
  help=_t("Default template used at collection creation."),
  type=str,
  default=os.path.join(os.path.dirname(__file__), '..', 'data', 'solrconfigs'))

CONFIG_INDEXING_TEMPLATES_PATH = Config(
  key="config_oozie_workspace_path",
  help=_t("oozie workspace template for indexing:"),
  type=str,
  default=os.path.join(os.path.dirname(__file__), '..', 'data', 'oozie_workspace')
  )

CONFIG_INDEXER_LIBS_PATH = Config(
  key="config_indexer_libs_path",
  help=_t("oozie workspace template for indexing:"),
  type=str,
  default='/tmp/smart_indexer_lib'
  )

SOLRCTL_PATH = Config(
  key="solrctl_path",
  help=_t("Location of the solrctl binary."),
  type=str,
  dynamic_default=solrctl)

# Deprecated and not used anymore
SOLR_ZK_ENSEMBLE = Config(
  key="solr_zk_ensemble",
  help=_t("Zookeeper ensemble."),
  type=str,
  dynamic_default=zkensemble)
