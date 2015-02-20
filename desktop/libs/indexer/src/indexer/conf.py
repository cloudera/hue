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

import os
from urlparse import urlparse

from django.utils.translation import ugettext_lazy as _t

from desktop.lib.conf import Config


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
    pass

  from search.conf import SOLR_URL
  parsed = urlparse(SOLR_URL.get())
  return "%s:2181/solr" % (parsed.hostname or 'localhost')



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

SOLRCTL_PATH = Config(
  key="solrctl_path",
  help=_t("Location of the solrctl binary."),
  type=str,
  dynamic_default=solrctl)

SOLR_ZK_ENSEMBLE  = Config(
  key="solr_zk_ensemble",
  help=_t("Zookeeper ensemble."),
  type=str,
  dynamic_default=zkensemble)
