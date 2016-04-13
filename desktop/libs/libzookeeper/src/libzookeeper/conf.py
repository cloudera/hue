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

from desktop.lib.conf import Config, coerce_string


LOG = logging.getLogger(__name__)


def zkensemble():
  """
  Try to guess the value if no values are specified.
  """

  from django.conf import settings

  if 'zookeeper' in settings.INSTALLED_APPS:
    try:
      # Backward compatibility until Hue 4
      from zookeeper.conf import CLUSTERS
      clusters = CLUSTERS.get()
      if clusters['default'].HOST_PORTS.get() != 'localhost:2181':
        return '%s' % clusters['default'].HOST_PORTS.get()
    except:
      LOG.warn('Could not get zookeeper ensemble from the zookeeper app')

  if 'search' in settings.INSTALLED_APPS:
    try:
      from search.conf import SOLR_URL
      parsed = urlparse(SOLR_URL.get())
      return "%s:2181" % (parsed.hostname or 'localhost')
    except:
      LOG.warn('Could not get zookeeper ensemble from the search app')

  return "localhost:2181"


ENSEMBLE=Config(
    "ensemble",
    help="ZooKeeper ensemble. Comma separated list of Host/Port, e.g. localhost:2181,localhost:2182,localhost:2183",
    dynamic_default=zkensemble,
    type=coerce_string,
)

PRINCIPAL_NAME=Config(
    "principal_name",
    help="Name of Kerberos principal when using security",
    default="zookeeper",
    type=str,
)
