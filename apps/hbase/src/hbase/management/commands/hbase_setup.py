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

from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from desktop.lib.paths import get_apps_root

from useradmin.models import install_sample_user

from hbased.ttypes import AlreadyExists
from hbase.api import HbaseApi


LOG = logging.getLogger(__name__)


class Command(BaseCommand):
  help = 'Create and fill some demo tables in the first configured cluster.'
  args = '<username>'

  def handle(self, *args, **options):
    if args:
      user = args[0]
    elif options and options['user']:
      user = options['user']
    else:
      user = install_sample_user()

    api = HbaseApi(user=user)
    cluster_name = api.getClusters()[0]['name'] # Currently pick first configured cluster

    # Check connectivity
    api.connectCluster(cluster_name)

    self.create_analytics_table(api, cluster_name)
    self.load_analytics_table(api, cluster_name)

    self.create_binary_table(api, cluster_name)
    self.load_binary_table(api, cluster_name)


  def create_analytics_table(self, api, cluster_name):
    try:
      api.createTable(cluster_name, 'analytics_demo', [{'properties': {'name': 'hour'}}, {'properties': {'name': 'day'}}, {'properties': {'name': 'total'}}])
    except AlreadyExists:
      pass

  def load_analytics_table(self, api, cluster_name):
    table_data = os.path.join(get_apps_root(), 'hbase', 'example', 'analytics', 'hbase-analytics.tsv')
    api.bulkUpload(cluster_name, 'analytics_demo', open(table_data))

  def create_binary_table(self, api, cluster_name):
    try:
      api.createTable(cluster_name, 'document_demo', [{'properties': {'name': 'doc'}}])
    except AlreadyExists:
      pass

  def load_binary_table(self, api, cluster_name):
    today = datetime.now().strftime('%Y%m%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y%m%d')

    api.putRow(cluster_name, 'document_demo', today, {'doc:txt': 'Hue is awesome!'})
    api.putRow(cluster_name, 'document_demo', today, {'doc:json': '{"user": "hue", "coolness": "extra"}'})
    api.putRow(cluster_name, 'document_demo', tomorrow, {'doc:version': '<xml>I like HBase</xml>'})
    api.putRow(cluster_name, 'document_demo', tomorrow, {'doc:version': '<xml>I LOVE HBase</xml>'})

    root = os.path.join(get_apps_root(), 'hbase', 'example', 'documents')

    api.putRow(cluster_name, 'document_demo', today, {'doc:img': open(root + '/hue-logo.png', "rb").read()})
    api.putRow(cluster_name, 'document_demo', today, {'doc:html': open(root + '/gethue.com.html', "rb").read()})
    api.putRow(cluster_name, 'document_demo', today, {'doc:pdf': open(root + '/gethue.pdf', "rb").read()})
